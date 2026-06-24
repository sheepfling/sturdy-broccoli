#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path.cwd()


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla.verification.repo_internal.verification.pitch_202x_certification import write_pitch_202x_certification


def _command_from_env(name: str, default: list[str]) -> list[str]:
    raw = os.environ.get(name)
    if not raw:
        return default
    return shlex.split(raw)


def _run(label: str, command: list[str], *, cwd: Path, env: dict[str, str]) -> dict[str, object]:
    start = time.monotonic()
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    duration = time.monotonic() - start
    return {
        "id": label,
        "label": label.replace("-", " "),
        "command": " ".join(shlex.quote(part) for part in command),
        "exit_code": int(result.returncode),
        "duration_seconds": duration,
        "stdout_tail": "\n".join(result.stdout.splitlines()[-20:]),
        "stderr_tail": "\n".join(result.stderr.splitlines()[-20:]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the Pitch 202X vendor-credence certification packet over the trial-safe real-runtime lanes."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Repository root used for analysis artifact locations.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for generated certification artifacts.",
    )
    args = parser.parse_args(argv)

    project_root = args.project_root.resolve()
    output_dir = (args.output_dir or (project_root / "analysis" / "pitch_202x_certification")).resolve()
    shell_env = os.environ.copy()
    python_cmd = os.environ.get("PYTHON", sys.executable)

    commands: list[tuple[str, list[str]]] = [
        (
            "preflight",
            _command_from_env(
                "HLA2010_PITCH_202X_CERTIFY_PREFLIGHT_CMD",
                ["bash", str(project_root / "tools" / "pitch"), "preflight"],
            ),
        ),
        (
            "surface-audit",
            _command_from_env(
                "HLA2010_PITCH_202X_CERTIFY_SURFACE_CMD",
                [python_cmd, str(project_root / "scripts" / "report_pitch_202x_surface.py")],
            ),
        ),
        (
            "smoke",
            _command_from_env(
                "HLA2010_PITCH_202X_CERTIFY_SMOKE_CMD",
                ["bash", str(project_root / "tools" / "pitch"), "smoke"],
            ),
        ),
        (
            "time-window-future-exclusion",
            _command_from_env(
                "HLA2010_PITCH_202X_CERTIFY_TIME_WINDOW_CMD",
                ["bash", str(project_root / "tools" / "pitch"), "time-window-probe"],
            ),
        ),
        (
            "time-window-restore-state",
            _command_from_env(
                "HLA2010_PITCH_202X_CERTIFY_RESTORE_STATE_CMD",
                ["bash", str(project_root / "tools" / "pitch"), "time-window-restore-state-probe"],
            ),
        ),
    ]

    runs: list[dict[str, object]] = []
    exit_code = 0
    for label, command in commands:
        run = _run(label, command, cwd=project_root, env=shell_env)
        runs.append(run)
        if int(run["exit_code"]) != 0 and exit_code == 0:
            exit_code = int(run["exit_code"])
        if label == "preflight" and int(run["exit_code"]) != 0:
            break

    paths = write_pitch_202x_certification(output_dir, project_root=project_root, command_runs=runs)
    print(paths.summary_json)
    print(paths.report_markdown)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
