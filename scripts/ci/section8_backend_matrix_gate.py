#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _usage() -> str:
    return "\n".join(
        [
            "usage: ./tools/section8-gate [pytest-args...]",
            "",
            "Canonical Section 8 backend-matrix gate:",
            "  ./tools/section8-gate",
            "",
            "Evidence:",
            "- tests/time/test_section8_backend_matrix.py",
            "- analysis/compliance/section8_backend_matrix.{json,md}",
        ]
    )


def _python_bin() -> str:
    venv_python = ROOT / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def _workspace_pythonpath() -> str:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    return os.pathsep.join(str(ROOT / rel) for rel in source_roots)


def _workspace_env() -> dict[str, str]:
    env = os.environ.copy()
    workspace_pythonpath = _workspace_pythonpath()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{workspace_pythonpath}{os.pathsep}{existing}" if existing else workspace_pythonpath
    )
    return env


def _run(argv: list[str]) -> int:
    return subprocess.run(argv, cwd=ROOT, env=_workspace_env(), check=False).returncode


def main(argv: list[str]) -> int:
    args = argv[1:]
    if args and args[0] in {"-h", "--help", "help"}:
        print(_usage())
        return 0

    python_bin = _python_bin()
    status = _run([python_bin, "-m", "pytest", "-q", "tests/time/test_section8_backend_matrix.py", *args])
    if status != 0:
        return status

    status = _run([python_bin, "scripts/generate_compliance_artifacts.py"])
    if status != 0:
        return status

    print(ROOT / "analysis" / "compliance" / "section8_backend_matrix.json")
    print(ROOT / "analysis" / "compliance" / "section8_backend_matrix.md")
    print("updated analysis/compliance/section8_backend_matrix.json")
    print("updated analysis/compliance/section8_backend_matrix.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
