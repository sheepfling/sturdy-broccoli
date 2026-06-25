#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run_step(title: str, argv: list[str]) -> int:
    print(f"[repo-green] {title}: {' '.join(argv)}", flush=True)
    result = subprocess.run(argv, cwd=ROOT, check=False)
    return result.returncode


def _usage() -> str:
    return "\n".join(
        [
            "usage: ./scripts/ci/repo_green.py",
            "",
            "Run the repo-green verification lane.",
            "",
            "- validates the test-surface manifest before broader orchestration",
            "- delegates to ./scripts/ci/full_sequence.py",
            "- keeps vendor runtime checks repo-green friendly",
            "- blocked CERTI/Pitch prerequisites skip cleanly after mandatory preflight",
            "- always emits normalized vendor runtime status and parity artifacts on exit",
            "",
            "Use ./scripts/ci/vendor_green.py for the strict real-runtime lane.",
        ]
    )


def main(argv: list[str]) -> int:
    args = argv[1:]
    if args and args[0] in {"-h", "--help", "help"}:
        print(_usage())
        return 0

    validator = os.environ.get(
        "HLA2010_REPO_GREEN_MANIFEST_VALIDATE_CMD",
        str(ROOT / "scripts" / "validate_test_surface_manifest.py"),
    )
    validator_argv = [sys.executable, validator] if Path(validator).suffix == ".py" else [validator]
    status = _run_step("validate test-surface manifest", validator_argv)
    if status != 0:
        subprocess.run([str(ROOT / "scripts" / "ci" / "emit_vendor_runtime_reports.sh"), "repo-green", "all"], cwd=ROOT, check=False)
        return status

    delegate = os.environ.get("HLA2010_REPO_GREEN_DELEGATE", str(ROOT / "scripts" / "ci" / "full_sequence.py"))
    delegate_argv = [sys.executable, delegate, *args] if Path(delegate).suffix == ".py" else [delegate, *args]
    status = _run_step("run full sequence", delegate_argv)
    subprocess.run([str(ROOT / "scripts" / "ci" / "emit_vendor_runtime_reports.sh"), "repo-green", "all"], cwd=ROOT, check=False)
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
