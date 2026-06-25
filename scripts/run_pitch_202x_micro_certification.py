from __future__ import annotations

import argparse
import json
import os
import shlex
import signal
import subprocess
import sys
import time
import tomllib
from pathlib import Path
from typing import Any

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla.verification.repo_internal.verification.pitch_202x_micro_certification import (
    PITCH_202X_MICRO_BACKENDS,
    write_pitch_202x_micro_certification,
)


def _python_bin() -> str:
    venv_python = SCRIPT_REPO_ROOT / ".venv" / "bin" / "python"
    if venv_python.is_file() and os.access(venv_python, os.X_OK):
        return str(venv_python)
    return sys.executable


def _default_commands(output_dir: Path) -> list[tuple[str, str, list[str]]]:
    micro_dir = output_dir / "micro_parity"
    command = [
        _python_bin(),
        str(SCRIPT_REPO_ROOT / "scripts" / "run_siso_pitch_micro_parity.py"),
        "--output-dir",
        str(micro_dir),
        "--require-real-vendor-preflight",
    ]
    for backend in PITCH_202X_MICRO_BACKENDS:
        command.extend(["--backend", backend])
    return [
        ("preflight", "preflight", ["bash", "./tools/pitch", "preflight"]),
        ("micro-parity", "micro parity", command),
    ]


def _split_command_with_spaceful_executable(raw: str) -> list[str]:
    for index, character in enumerate(raw):
        if character != " ":
            continue
        executable = raw[:index]
        if not executable:
            continue
        executable_path = Path(executable)
        if not executable_path.exists():
            continue
        remainder = raw[index + 1 :].strip()
        parts = [str(executable_path)]
        if remainder:
            parts.extend(shlex.split(remainder))
        return parts
    return []


def _env_command(name: str) -> list[str] | None:
    value = os.environ.get(name)
    if not value:
        return None
    parts = shlex.split(value)
    if parts and Path(parts[0]).exists():
        return parts
    recovered = _split_command_with_spaceful_executable(value)
    if recovered:
        return recovered
    return parts


def _has_flag(args: list[str], flag: str) -> bool:
    return any(part == flag or part.startswith(f"{flag}=") for part in args)


def _terminate_process_group(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=5)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    process.wait(timeout=5)


def _run_command(
    command: list[str],
    *,
    completion_artifact: Path | None = None,
) -> tuple[int, float]:
    started = time.perf_counter()
    process = subprocess.Popen(
        command,
        cwd=SCRIPT_REPO_ROOT,
        start_new_session=True,
        text=True,
    )
    artifact_grace_seconds = float(os.environ.get("HLA2010_PITCH_202X_MICRO_CERTIFY_ARTIFACT_GRACE_SECONDS", "10"))
    artifact_seen_at: float | None = None
    while True:
        exit_code = process.poll()
        if exit_code is not None:
            return exit_code, time.perf_counter() - started
        if completion_artifact is not None and completion_artifact.exists():
            if artifact_seen_at is None:
                artifact_seen_at = time.perf_counter()
            elif (time.perf_counter() - artifact_seen_at) >= artifact_grace_seconds:
                _terminate_process_group(process)
                return 0, time.perf_counter() - started
        time.sleep(1.0)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the bounded Pitch 202X micro comparison packet.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd() / "artifacts" / "pitch_202x_micro_certification",
        help="Directory for the certification summary, comparison CSV, and markdown report.",
    )
    args = parser.parse_args(argv)

    output_dir = args.output_dir.resolve()
    micro_dir = output_dir / "micro_parity"
    micro_summary_path = micro_dir / "siso_pitch_micro_parity_summary.json"
    runs: list[dict[str, Any]] = []
    default_commands = _default_commands(output_dir)
    for run_id, label, default_command in default_commands:
        env_name = f"HLA2010_PITCH_202X_MICRO_CERTIFY_{run_id.upper().replace('-', '_')}_CMD"
        command = _env_command(env_name) or default_command
        if run_id == "micro-parity" and not _has_flag(command, "--output-dir"):
            command = [*command, "--output-dir", str(micro_dir)]
        exit_code, duration = _run_command(
            command,
            completion_artifact=micro_summary_path if run_id == "micro-parity" else None,
        )
        runs.append(
            {
                "id": run_id,
                "label": label,
                "command": " ".join(shlex.quote(part) for part in command),
                "exit_code": exit_code,
                "duration_seconds": duration,
            }
        )
        if exit_code != 0:
            break

    if not micro_summary_path.exists():
        raise SystemExit(f"expected micro parity summary at {micro_summary_path}")
    micro_summary = json.loads(micro_summary_path.read_text(encoding="utf-8"))

    paths = write_pitch_202x_micro_certification(
        output_dir,
        project_root=SCRIPT_REPO_ROOT,
        micro_summary=micro_summary,
        command_runs=runs,
    )
    print(paths.summary_json)
    print(paths.comparison_csv)
    print(paths.report_markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
