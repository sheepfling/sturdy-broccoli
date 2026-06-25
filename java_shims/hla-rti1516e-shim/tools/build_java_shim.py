#!/usr/bin/env python3
"""Build the tiny hla.rti1516e Java shim jar used by optional bridge tests."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path


def _require_usable_tool(path: str | None, name: str) -> str:
    if path is None:
        raise SystemExit(f"{name} is required to build the Java shim")
    version_flag = "--version" if name == "jar" else "-version"
    try:
        completed = subprocess.run([path, version_flag], capture_output=True, text=True, check=False)
    except OSError as exc:
        raise SystemExit(f"{name} is not executable: {path}") from exc
    if completed.returncode != 0:
        raise SystemExit(
            f"{name} is not usable on this host: {path}\n"
            f"stdout: {completed.stdout.strip()}\n"
            f"stderr: {completed.stderr.strip()}"
        )
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Path to the output jar")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    repo_root = root.parents[1]
    pyproject = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    for relative in reversed(pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]):
        sys.path.insert(0, str(repo_root / relative))
    from hla.bridges.java.common.java_runtime import discover_java_tool, ensure_java_home

    src_root = root / "src" / "main" / "java"
    sources = sorted(str(path) for path in src_root.rglob("*.java"))
    if not sources:
        raise SystemExit(f"No Java sources found below {src_root}")

    ensure_java_home()
    javac = _require_usable_tool(discover_java_tool("javac"), "javac")
    jar = _require_usable_tool(discover_java_tool("jar"), "jar")

    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="hla-rti1516e-shim-") as tmp:
        classes = Path(tmp) / "classes"
        classes.mkdir(parents=True)
        subprocess.run([javac, "-Xlint:unchecked", "-d", str(classes), *sources], check=True)
        subprocess.run([jar, "cf", str(out), "-C", str(classes), "."], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
