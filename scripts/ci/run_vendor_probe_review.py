#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Sequence

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[2]


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()


def _default_stability_command() -> str:
    return str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_probe_stability.sh")


def _default_promotion_command() -> str:
    return f'python3 "{SCRIPT_REPO_ROOT / "scripts" / "ci" / "write_vendor_probe_promotion_review.py"}"'


def _default_parity_command() -> str:
    return f'python3 "{SCRIPT_REPO_ROOT / "scripts" / "run_vendor_parity_artifacts.py"}"'


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


def _resolve_command_argv(command_text: str, extra_args: Sequence[str] = ()) -> list[str]:
    raw_path = Path(command_text)
    if raw_path.is_file():
        if raw_path.suffix == ".sh":
            return ["bash", str(raw_path), *extra_args]
        return [str(raw_path), *extra_args]
    tokens = shlex.split(command_text)
    if (not tokens or not Path(tokens[0]).exists()) and " " in command_text:
        recovered = _split_command_with_spaceful_executable(command_text)
        if recovered:
            tokens = recovered
    if not tokens:
        raise ValueError("command text resolved to no argv tokens")
    command_path = Path(tokens[0])
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


def _run_command(command_text: str, *, extra_args: Sequence[str], env: dict[str, str]) -> int:
    argv = _resolve_command_argv(command_text, extra_args)
    completed = subprocess.run(
        argv,
        cwd=SCRIPT_REPO_ROOT,
        env=env,
        check=False,
    )
    return int(completed.returncode)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run repeated probe stability, promotion review, and parity refresh."
    )
    parser.add_argument("profile", help="Vendor probe profile to review.")
    parser.add_argument("repeat_count", nargs="?", default="5", help="Repeated-run count. Defaults to 5.")
    args = parser.parse_args(argv)

    env = _activate_virtualenv_env(os.environ.copy())
    stability_cmd = env.get("HLA2010_VENDOR_PROBE_REVIEW_STABILITY_CMD", _default_stability_command())
    promotion_cmd = env.get("HLA2010_VENDOR_PROBE_REVIEW_PROMOTION_CMD", _default_promotion_command())
    parity_cmd = env.get("HLA2010_VENDOR_PROBE_REVIEW_PARITY_CMD", _default_parity_command())

    status = _run_command(stability_cmd, extra_args=(args.profile, args.repeat_count), env=env)
    if status != 0:
        return status
    status = _run_command(promotion_cmd, extra_args=(), env=env)
    if status != 0:
        return status
    return _run_command(parity_cmd, extra_args=(), env=env)


if __name__ == "__main__":
    raise SystemExit(main())
