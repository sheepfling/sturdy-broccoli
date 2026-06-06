#!/usr/bin/env python3
"""Build the tiny hla.rti1516e Java shim jar used by optional bridge tests."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Path to the output jar")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    project_root = root.parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from hla2010.java_runtime import discover_java_tool, ensure_java_home

    src_root = root / "src" / "main" / "java"
    sources = sorted(str(path) for path in src_root.rglob("*.java"))
    if not sources:
        raise SystemExit(f"No Java sources found below {src_root}")

    ensure_java_home()
    javac = discover_java_tool("javac")
    jar = discover_java_tool("jar")
    if javac is None:
        raise SystemExit("javac is required to build the Java shim")
    if jar is None:
        raise SystemExit("jar is required to build the Java shim")

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
