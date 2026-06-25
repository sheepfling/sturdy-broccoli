#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _usage() -> str:
    return "\n".join(
        [
            "usage: ./scripts/ci/full_sequence.py",
            "",
            "Run the repo-green full documented local lifecycle sequence:",
            "install -> upstream contract -> compilation -> lint / type annotations -> repo-green smoke -> unit shards",
            "-> integration smoke -> integration tests -> compliance matrices",
            "-> full backend matrixed compliance -> other evidence",
            "",
            "Blocked vendor prerequisites still run mandatory preflight first and then skip",
            "cleanly. Use ./scripts/ci/vendor_green.py for strict real-runtime failure.",
        ]
    )


def _run_step(label: str, argv: list[str]) -> None:
    print(f"[full_sequence] {label}", file=sys.stderr)
    command = argv
    if argv and argv[0].endswith(".sh"):
        command = ["bash", *argv]
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main(argv: list[str]) -> int:
    args = argv[1:]
    if args and args[0] in {"help", "-h", "--help"}:
        print(_usage())
        return 0

    steps: list[tuple[str, list[str]]] = [
        ("install", [str(ROOT / "scripts" / "ci" / "install_python.sh")]),
        ("upstream contract", [str(ROOT / "scripts" / "ci" / "upstream_contract.sh")]),
        ("compilation", [str(ROOT / "scripts" / "ci" / "lint.sh")]),
        ("lint / type annotations", [str(ROOT / "scripts" / "ci" / "pyright.sh")]),
        ("standard shim route artifacts", [str(ROOT / "scripts" / "ci" / "build_standard_shims_if_available.sh")]),
        ("repo-green smoke", ["bash", str(ROOT / "tools" / "python"), "verify-smoke"]),
        ("unit shard sweep", ["bash", str(ROOT / "tools" / "test-surface"), "run", "repo-green-units"]),
        ("integration smoke", [sys.executable, str(ROOT / "scripts" / "ci" / "vendor_runtime_smoke.py"), "matrix"]),
        ("integration tests", [sys.executable, str(ROOT / "scripts" / "run_two_federate_suite.py")]),
        ("other tests", [str(ROOT / "scripts" / "ci" / "target_radar_backend_matrix.sh")]),
        ("other tests", [str(ROOT / "scripts" / "ci" / "target_radar_proof.sh")]),
        ("Proto2025 FOM showcase", [str(ROOT / "scripts" / "ci" / "proto2025_fom_showcase.sh")]),
        ("compliance matrices", [str(ROOT / "scripts" / "ci" / "section8_backend_matrix_gate.sh")]),
        ("full backend matrixed compliance", [sys.executable, str(ROOT / "scripts" / "ci" / "vendor_runtime_smoke.py"), "all"]),
    ]
    for label, step_argv in steps:
        _run_step(label, step_argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
