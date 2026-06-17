from __future__ import annotations

import importlib.util
import json
import sys
from argparse import Namespace
from pathlib import Path

from hla.bridges.java.common import JavaToolchainArtifact, JavaToolchainInventory


ROOT = Path(__file__).resolve().parents[2]


def _load_hla_x_module():
    spec = importlib.util.spec_from_file_location("hla_x_module_for_tests", ROOT / "scripts" / "hla_x.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_java_toolchain_inventory_reports_tools_and_artifacts(tmp_path: Path, monkeypatch, capsys) -> None:
    repo_root = tmp_path / "repo"
    java_home = tmp_path / "jdk"
    java_bin = java_home / "bin" / "java"
    javac_bin = java_home / "bin" / "javac"
    jar_bin = java_home / "bin" / "jar"
    java_bin.parent.mkdir(parents=True)
    java_bin.write_text("")
    javac_bin.write_text("")
    jar_bin.write_text("")

    java_2010 = repo_root / "build/rosetta/java-standard-2010/hla-x-rti1516e-java-shim.jar"
    java_2025 = repo_root / "build/rosetta/java-standard-2025/hla-x-rti1516-2025-java-shim.jar"
    java_2010.parent.mkdir(parents=True)
    java_2025.parent.mkdir(parents=True)
    java_2010.write_text("jar")
    java_2025.write_text("jar")

    artifact_2010 = JavaToolchainArtifact(
        key="java-standard-2010",
        label="Java 2010 standard shim jar",
        path=str(java_2010),
        exists=True,
        build_command="./tools/hla-x build java-standard-2010",
    )
    artifact_2025 = JavaToolchainArtifact(
        key="java-standard-2025",
        label="Java 2025 standard shim jar",
        path=str(java_2025),
        exists=True,
        build_command="./tools/hla-x build java-standard-2025",
    )
    inventory = JavaToolchainInventory(
        java_home_env=str(java_home),
        jdk_home_env=None,
        discovery_source="JAVA_HOME",
        java_home=str(java_home),
        java=str(java_bin),
        javac=str(javac_bin),
        jar=str(jar_bin),
        java_ok=True,
        javac_ok=True,
        jar_ok=True,
        status="ready",
        artifacts=(artifact_2010, artifact_2025),
        notes=("Java home discovered from JAVA_HOME",),
    )

    from hla.bridges.java import common as java_common

    monkeypatch.setattr(java_common, "discover_java_toolchain", lambda repo_root_arg: inventory)

    module = _load_hla_x_module()
    output_dir = tmp_path / "reports"
    rc = module.main(["java", "doctor", "--output-dir", str(output_dir)])
    assert rc == 0

    json_path = output_dir / "java-toolchain.json"
    md_path = output_dir / "java-toolchain.md"
    assert json_path.exists()
    assert md_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["status"] == "ready"
    assert payload["java_ok"] is True
    assert payload["javac_ok"] is True
    assert payload["jar_ok"] is True
    assert payload["artifacts"][0]["exists"] is True

    stdout_payload = json.loads(capsys.readouterr().out)
    assert stdout_payload["evidence_json"] == str(json_path)
    assert stdout_payload["evidence_markdown"] == str(md_path)
    assert stdout_payload["recommended_commands"] == []

    rendered = md_path.read_text(encoding="utf-8")
    assert "# Java Toolchain Inventory" in rendered
    assert "Java 2010 standard shim jar" in rendered
    assert "Java 2025 standard shim jar" in rendered
    assert "./tools/hla-x build java-standard-2010" in rendered
    assert "./tools/hla-x build java-standard-2025" in rendered
