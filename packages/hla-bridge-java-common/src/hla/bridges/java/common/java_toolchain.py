"""Java toolchain discovery and inventory reporting."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .java_runtime import discover_java_home_with_source, discover_java_tool


JAVA_2010_JAR = Path(
    os.environ.get(
        "HLA_X_JAVA_STANDARD_2010_JAR",
        "build/rosetta/java-standard-2010/hla-x-rti1516e-java-shim.jar",
    )
)
JAVA_2025_JAR = Path(
    os.environ.get(
        "HLA_X_JAVA_STANDARD_2025_JAR",
        "build/rosetta/java-standard-2025/hla-x-rti1516-2025-java-shim.jar",
    )
)


@dataclass(frozen=True, slots=True)
class JavaToolchainArtifact:
    key: str
    label: str
    path: str
    exists: bool
    build_command: str


@dataclass(frozen=True, slots=True)
class JavaToolchainInventory:
    java_home_env: str | None
    jdk_home_env: str | None
    discovery_source: str | None
    java_home: str | None
    java: str | None
    javac: str | None
    jar: str | None
    java_ok: bool
    javac_ok: bool
    jar_ok: bool
    status: str
    artifacts: tuple[JavaToolchainArtifact, ...]
    notes: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == "ready"

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


def _artifact(key: str, label: str, path: Path, build_command: str) -> JavaToolchainArtifact:
    return JavaToolchainArtifact(
        key=key,
        label=label,
        path=str(path),
        exists=path.exists(),
        build_command=build_command,
    )


def discover_java_toolchain(repo_root: Path) -> JavaToolchainInventory:
    java_home, discovery_source = discover_java_home_with_source()
    java_home_env = os.environ.get("JAVA_HOME")
    jdk_home_env = os.environ.get("JDK_HOME")

    java = discover_java_tool("java")
    javac = discover_java_tool("javac")
    jar = discover_java_tool("jar")

    artifacts = (
        _artifact(
            "java-standard-2010",
            "Java 2010 standard shim jar",
            repo_root / JAVA_2010_JAR,
            "./tools/hla-x build java-standard-2010",
        ),
        _artifact(
            "java-standard-2025",
            "Java 2025 standard shim jar",
            repo_root / JAVA_2025_JAR,
            "./tools/hla-x build java-standard-2025",
        ),
    )

    java_ok = java is not None
    javac_ok = javac is not None
    jar_ok = jar is not None
    artifact_ok = all(item.exists for item in artifacts)

    notes: list[str] = []
    warnings: list[str] = []
    if discovery_source is None:
        warnings.append("no Java home was discovered; set JAVA_HOME or JDK_HOME, or install a JDK")
    else:
        notes.append(f"Java home discovered from {discovery_source}")
    if not java_ok or not javac_ok or not jar_ok:
        warnings.append("one or more Java tools are missing from the discovery path")
    if not artifact_ok:
        warnings.append("one or more Rosetta Java shim jars are missing; build them with ./tools/hla-x build <target>")

    if java_ok and javac_ok and jar_ok and artifact_ok:
        status = "ready"
    elif java_ok or javac_ok or jar_ok or java_home is not None:
        status = "degraded"
    else:
        status = "blocked"

    return JavaToolchainInventory(
        java_home_env=java_home_env,
        jdk_home_env=jdk_home_env,
        discovery_source=discovery_source,
        java_home=str(java_home) if java_home is not None else None,
        java=java,
        javac=javac,
        jar=jar,
        java_ok=java_ok,
        javac_ok=javac_ok,
        jar_ok=jar_ok,
        status=status,
        artifacts=artifacts,
        notes=tuple(notes),
        warnings=tuple(warnings),
    )


def render_java_toolchain_markdown(inventory: JavaToolchainInventory) -> str:
    def verdict(value: bool) -> str:
        return "PASS" if value else "FAIL"

    lines = [
        "# Java Toolchain Inventory",
        "",
        f"- Status: `{inventory.status}`",
        f"- Discovery source: `{inventory.discovery_source or ''}`",
        f"- JAVA_HOME env: `{inventory.java_home_env or ''}`",
        f"- JDK_HOME env: `{inventory.jdk_home_env or ''}`",
        f"- Java home: `{inventory.java_home or ''}`",
        f"- java: `{inventory.java or ''}`",
        f"- javac: `{inventory.javac or ''}`",
        f"- jar: `{inventory.jar or ''}`",
        "",
        "## Tool Checks",
        "",
        f"- java: {verdict(inventory.java_ok)}",
        f"- javac: {verdict(inventory.javac_ok)}",
        f"- jar: {verdict(inventory.jar_ok)}",
        "",
        "## Rosetta Artifacts",
        "",
        "| key | label | path | exists | build command |",
        "| --- | --- | --- | --- | --- |",
    ]
    for artifact in inventory.artifacts:
        lines.append(
            f"| `{artifact.key}` | {artifact.label} | `{artifact.path}` | {verdict(artifact.exists)} | `{artifact.build_command}` |"
        )
    lines.extend(["", "## Notes", ""])
    if inventory.notes:
        lines.extend(f"- {note}" for note in inventory.notes)
    else:
        lines.append("- none")
    lines.extend(["", "## Warnings", ""])
    if inventory.warnings:
        lines.extend(f"- {warning}" for warning in inventory.warnings)
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def write_java_toolchain_reports(inventory: JavaToolchainInventory, output_dir: str | Path) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "java-toolchain.json"
    md_path = output / "java-toolchain.md"
    json_path.write_text(json.dumps(inventory.to_json_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_java_toolchain_markdown(inventory), encoding="utf-8")
    return json_path, md_path


__all__ = [
    "JAVA_2010_JAR",
    "JAVA_2025_JAR",
    "JavaToolchainArtifact",
    "JavaToolchainInventory",
    "discover_java_toolchain",
    "render_java_toolchain_markdown",
    "write_java_toolchain_reports",
]
