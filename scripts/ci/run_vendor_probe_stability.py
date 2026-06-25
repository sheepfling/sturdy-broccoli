#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
import shlex
import subprocess
import sys
import time
import tomllib
from pathlib import Path
from typing import Sequence

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path.cwd()


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla.verification.repo_internal.verification.vendor_probe_stability import canonical_operator_command


def _resolve_command_argv(command_text: str, extra_args: Sequence[str] = ()) -> list[str]:
    raw_path = Path(command_text)
    if raw_path.is_file():
        if raw_path.suffix == ".py":
            return [sys.executable, str(raw_path), *extra_args]
        if raw_path.suffix == ".sh":
            return ["bash", str(raw_path), *extra_args]
        return [str(raw_path), *extra_args]
    tokens = shlex.split(command_text)
    if not tokens:
        raise ValueError("command text resolved to no argv tokens")
    command_path = Path(tokens[0])
    if command_path.is_file() and command_path.suffix == ".py":
        return [sys.executable, str(command_path), *tokens[1:], *extra_args]
    if command_path.is_file() and command_path.suffix == ".sh":
        return ["bash", str(command_path), *tokens[1:], *extra_args]
    if command_path.is_file():
        return [str(command_path), *tokens[1:], *extra_args]
    return [*tokens, *extra_args]


def _activate_virtualenv_env(base_env: dict[str, str]) -> dict[str, str]:
    env = dict(base_env)
    venv_dir = SCRIPT_REPO_ROOT / ".venv"
    python_bin = venv_dir / "bin" / "python3"
    bin_dir = venv_dir / "bin"
    if python_bin.exists():
        env["VIRTUAL_ENV"] = str(venv_dir)
        env["PATH"] = os.pathsep.join((str(bin_dir), env.get("PATH", "")))
    return env


def _ci_state_profile(profile: str) -> str:
    if profile in {
        "certi",
        "certi-patched",
        "certi-upstream",
        "certi-compare",
        "certi-save-restore",
        "certi-save-restore-probe",
        "certi-ddm",
        "certi-ddm-probe",
    }:
        return "certi"
    if profile in {
        "pitch",
        "pitch-smoke",
        "pitch-verify",
        "pitch-save-restore",
        "pitch-save-restore-probe",
        "pitch-ddm",
        "pitch-ddm-probe",
        "pitch-negotiated",
        "pitch-negotiated-probe",
        "pitch-time-window-probe",
        "pitch-time-window-restore-state-probe",
        "pitch-lost-federate",
        "pitch-lost-federate-probe",
    }:
        return "pitch"
    if profile == "matrix":
        return "matrix"
    if profile == "vendor-edge":
        return "vendor-edge"
    return "all"


def _should_validate_ci_state(requirement: str, env: dict[str, str]) -> bool:
    value = requirement.lower()
    if value in {"1", "true", "yes", "always"}:
        return True
    if value in {"0", "false", "no", "never"}:
        return False
    if value == "auto":
        return env.get("GITHUB_ACTIONS") == "true"
    raise ValueError(f"unsupported HLA2010_VENDOR_PROBE_REQUIRE_CI_STATE value: {requirement}")


def _run_command(
    command_text: str,
    *,
    extra_args: Sequence[str],
    env: dict[str, str],
    stdout_path: Path | None = None,
    stderr_path: Path | None = None,
) -> int:
    argv = _resolve_command_argv(command_text, extra_args)
    if stdout_path is None and stderr_path is None:
        completed = subprocess.run(argv, cwd=SCRIPT_REPO_ROOT, env=env, check=False)
        return int(completed.returncode)
    with (stdout_path.open("w", encoding="utf-8") if stdout_path else open(os.devnull, "w", encoding="utf-8")) as stdout_handle:
        with (stderr_path.open("w", encoding="utf-8") if stderr_path else open(os.devnull, "w", encoding="utf-8")) as stderr_handle:
            completed = subprocess.run(
                argv,
                cwd=SCRIPT_REPO_ROOT,
                env=env,
                stdout=stdout_handle,
                stderr=stderr_handle,
                text=True,
                check=False,
            )
    return int(completed.returncode)


def _write_attempts_csv(path: Path, attempts: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("iteration", "exit_code", "duration_seconds", "stdout_path", "stderr_path"),
        )
        writer.writeheader()
        for row in attempts:
            writer.writerow(row)


def _replay_attempt_logs(attempts: Sequence[dict[str, object]]) -> None:
    for row in attempts:
        stdout_path = Path(str(row["stdout_path"]))
        stderr_path = Path(str(row["stderr_path"]))
        if stdout_path.exists():
            sys.stdout.write(stdout_path.read_text(encoding="utf-8", errors="replace"))
        if stderr_path.exists():
            sys.stderr.write(stderr_path.read_text(encoding="utf-8", errors="replace"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a vendor profile repeatedly and emit stability artifacts."
    )
    parser.add_argument("profile", help="Vendor profile to exercise repeatedly.")
    parser.add_argument("repeat_count", nargs="?", default="3", help="Repeated-run count. Defaults to 3.")
    args = parser.parse_args(argv)

    env = _activate_virtualenv_env(os.environ.copy())
    repeat_count = int(args.repeat_count)
    profile = args.profile
    vendor_green_cmd = env.get(
        "HLA2010_VENDOR_PROBE_STABILITY_VENDOR_GREEN",
        str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"),
    )
    output_base_dir = Path(
        env.get("HLA2010_VENDOR_PROBE_STABILITY_DIR", str(PROJECT_ROOT / "artifacts" / "vendor_probe_stability"))
    )
    ci_state_output_dir = Path(
        env.get("HLA2010_VENDOR_RUNTIME_CI_STATE_DIR", str(PROJECT_ROOT / "artifacts" / "vendor_runtime_ci_state"))
    )
    ci_state_required = env.get("HLA2010_VENDOR_PROBE_REQUIRE_CI_STATE", "auto")
    ci_state_cmd = env.get("HLA2010_VENDOR_PROBE_CI_STATE_CMD", "")

    if _should_validate_ci_state(ci_state_required, env):
        ci_profile = _ci_state_profile(profile)
        ci_command = ci_state_cmd or f'python3 "{SCRIPT_REPO_ROOT / "scripts" / "ci" / "check_vendor_runtime_ci_state.py"}"'
        status = _run_command(
            ci_command,
            extra_args=("--profile", ci_profile, "--output-dir", str(ci_state_output_dir)),
            env=env,
        )
        if status != 0:
            return status

    profile_output_dir = output_base_dir / profile
    logs_dir = profile_output_dir / "logs"
    profile_output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    attempts: list[dict[str, object]] = []
    overall_status = 0
    for iteration in range(1, repeat_count + 1):
        stdout_path = logs_dir / f"attempt-{iteration}.stdout.txt"
        stderr_path = logs_dir / f"attempt-{iteration}.stderr.txt"
        run_env = dict(env)
        run_env["HLA2010_VENDOR_GREEN_REQUIRE_CI_STATE"] = "0"
        start = time.monotonic()
        status = _run_command(
            vendor_green_cmd,
            extra_args=(profile,),
            env=run_env,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
        )
        duration = int(time.monotonic() - start)
        attempts.append(
            {
                "iteration": iteration,
                "exit_code": status,
                "duration_seconds": duration,
                "stdout_path": str(stdout_path),
                "stderr_path": str(stderr_path),
            }
        )
        if status != 0:
            overall_status = 1

    _replay_attempt_logs(attempts)
    attempts_file = profile_output_dir / "attempts.csv"
    _write_attempts_csv(attempts_file, attempts)

    write_cmd = f'python3 "{SCRIPT_REPO_ROOT / "scripts" / "ci" / "write_vendor_probe_stability.py"}"'
    status = _run_command(
        write_cmd,
        extra_args=(
            "--profile",
            profile,
            "--repeat-count",
            str(repeat_count),
            "--command",
            canonical_operator_command(profile),
            "--executor-command",
            f"{vendor_green_cmd} {profile}",
            "--attempts-file",
            str(attempts_file),
            "--output-dir",
            str(profile_output_dir),
        ),
        env=env,
    )
    if status != 0:
        return status
    return overall_status


if __name__ == "__main__":
    raise SystemExit(main())
