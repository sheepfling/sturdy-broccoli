#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
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

from hla.verification.repo_internal.verification.workspace_two_federate_suite import write_workspace_two_federate_suite_artifacts


def _apply_pitch_preflight_runtime_env() -> None:
    artifact_dir = Path(os.environ.get("HLA2010_PREFLIGHT_ARTIFACT_DIR", str(PROJECT_ROOT / "artifacts" / "preflight_artifacts")))
    artifact_path = artifact_dir / "pitch-preflight.json"
    if not artifact_path.exists():
        return
    max_age_seconds = float(os.environ.get("HLA2010_PREFLIGHT_MAX_AGE_SECONDS", "43200"))
    try:
        if max_age_seconds > 0 and (time.time() - artifact_path.stat().st_mtime) > max_age_seconds:
            return
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if (
        str(payload.get("tool", "")) != "pitch-preflight"
        or int(payload.get("exit_code", 1)) != 0
        or str(payload.get("environment", "")) != "ready"
    ):
        return
    ports = payload.get("ports") or {}
    runtime = payload.get("runtime") or {}
    crc = ports.get("crc") or {}
    fedpro = ports.get("fedpro") or {}
    os.environ.setdefault("HLA2010_PITCH_PREFLIGHT_OK", "1")
    os.environ.setdefault("HLA2010_PITCH_CRC_MODE", "docker")
    os.environ.setdefault("HLA2010_PITCH_DOCKER_BUILD", "0")
    os.environ.setdefault("HLA2010_PITCH_DOCKER_ATTACH_EXISTING", "1")
    if runtime.get("container_name"):
        os.environ.setdefault("HLA2010_PITCH_DOCKER_NAME", str(runtime["container_name"]))
    if "port" in crc:
        os.environ.setdefault("HLA2010_PITCH_CRC_PORT", str(crc["port"]))
    if "port" in fedpro:
        os.environ.setdefault("HLA2010_PITCH_FEDPRO_PORT", str(fedpro["port"]))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the composite two-federate suite and write artifacts.")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "artifacts" / "two_federate_suite"),
        help="Directory for generated artifacts",
    )
    parser.add_argument("--target-radar-steps", type=int, default=4)
    args = parser.parse_args(argv)

    _apply_pitch_preflight_runtime_env()

    paths = write_workspace_two_federate_suite_artifacts(
        args.output_dir,
        target_radar_steps=args.target_radar_steps,
    )
    print(paths.summary_json)
    print(paths.track_reports_csv)
    print(paths.callbacks_csv)
    print(paths.report_markdown)
    print(paths.summary_svg)
    print(paths.timeline_svg)
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(exit_code)
