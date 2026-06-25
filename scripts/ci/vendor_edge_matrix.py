#!/usr/bin/env python3
from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALID = {"time-query", "negotiated-ownership", "save-restore", "ddm", "all"}


def _usage() -> str:
    return "\n".join(
        [
            "vendor_edge_matrix.py: run the highest-value vendor edge slice.",
            "",
            "Profiles:",
            "- time-query: CERTI time-query/FQR compare plus the Pitch time-profile smoke",
            "- negotiated-ownership: CERTI ownership compare plus the Pitch negotiated-ownership smoke",
            "- save-restore: CERTI and Pitch save/restore probe slices",
            "- ddm: CERTI and Pitch DDM probe slices",
            "- all: run both profiles in sequence and refresh the compliance packet",
            "",
            "Usage:",
            "  ./scripts/ci/vendor_edge_matrix.py [time-query|negotiated-ownership|save-restore|ddm|all]",
        ]
    )


def _run(argv: list[str]) -> None:
    result = subprocess.run(argv, cwd=ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def _run_compliance_generator(command: str) -> None:
    result = subprocess.run(shlex.split(command), cwd=ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def _command_argv(command: str, *extra_args: str) -> list[str]:
    path = Path(command)
    if path.is_file() and path.suffix == ".py":
        return [sys.executable, str(path), *extra_args]
    if path.is_file():
        return [str(path), *extra_args]
    return [command, *extra_args]


def main(argv: list[str]) -> int:
    args = argv[1:]
    if args and args[0] in {"-h", "--help", "help"}:
        print(_usage())
        return 0

    profile = args[0] if args else "all"
    if profile not in VALID:
        print("usage: ./scripts/ci/vendor_edge_matrix.py [time-query|negotiated-ownership|save-restore|ddm|all]", file=sys.stderr)
        return 2

    vendor_green = os.environ.get("HLA2010_VENDOR_EDGE_VENDOR_GREEN", str(ROOT / "scripts" / "ci" / "vendor_green.py"))
    compliance_generator = os.environ.get("HLA2010_VENDOR_EDGE_COMPLIANCE_GENERATOR", "python3 scripts/generate_compliance_artifacts.py")

    def run_time_query() -> None:
        _run(_command_argv(vendor_green, "certi-compare"))
        _run(_command_argv(vendor_green, "pitch-smoke"))

    def run_negotiated() -> None:
        _run(_command_argv(vendor_green, "certi-compare"))
        _run(_command_argv(vendor_green, "pitch-negotiated-probe"))

    def run_save_restore() -> None:
        _run(_command_argv(vendor_green, "certi-save-restore-probe"))
        _run(_command_argv(vendor_green, "pitch-save-restore-probe"))

    def run_ddm() -> None:
        _run(_command_argv(vendor_green, "certi-ddm-probe"))
        _run(_command_argv(vendor_green, "pitch-ddm-probe"))

    if profile == "time-query":
        run_time_query()
    elif profile == "negotiated-ownership":
        run_negotiated()
    elif profile == "save-restore":
        run_save_restore()
    elif profile == "ddm":
        run_ddm()
    elif profile == "all":
        run_time_query()
        run_negotiated()
        run_save_restore()
        run_ddm()

    _run_compliance_generator(compliance_generator)
    print("updated analysis/compliance/*.json")
    print("updated analysis/compliance/*.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
