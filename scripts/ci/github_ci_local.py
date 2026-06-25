#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALID_MODES = {"default", "vendor-required", "vendor-edge", "probe-review", "vendor-smoke", "all"}


def _usage() -> str:
    return "\n".join(
        [
            "usage: ./scripts/ci/github_ci_local.py [mode]",
            "",
            "Run GitHub CI lanes locally with stable top-to-bottom ordering.",
            "",
            "Modes:",
            "- default: lightweight contract guard plus the default GitHub Ubuntu stack",
            "- vendor-required: dedicated real-runtime required lanes (certi, pitch, matrix)",
            "- vendor-edge: dedicated vendor-edge matrix lanes",
            "- probe-review: dedicated repeated-run probe review lanes",
            "- vendor-smoke: explicit vendor-runtime-smoke workflow lanes",
            "- all: run every mode above in workflow order",
            "",
            "Examples:",
            "  ./scripts/ci/github_ci_local.py",
            "  ./scripts/ci/github_ci_local.py vendor-required",
            "  ./scripts/ci/github_ci_local.py all",
            "",
            "Notes:",
            "- default mirrors the repo's default GitHub Actions Ubuntu jobs.",
            "- the vendor-* modes are strict local reruns for machines with the real-runtime",
            "  prerequisites already configured.",
            "- each lane may be overridden for tests via",
            "  HLA2010_GITHUB_CI_LOCAL_<LANE_NAME>_CMD.",
        ]
    )


def _log(name: str) -> None:
    print(f"[github_ci_local] running {name}", file=sys.stderr)


def _run_lane(name: str, argv: list[str], env: dict[str, str]) -> None:
    override_var = f"HLA2010_GITHUB_CI_LOCAL_{name.upper().replace('-', '_')}_CMD"
    _log(name)
    override = env.get(override_var)
    if override:
        result = subprocess.run(["bash", "-lc", override], cwd=ROOT, env=env, check=False)
    else:
        result = subprocess.run(argv, cwd=ROOT, env=env, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def _run_default(env: dict[str, str]) -> None:
    _run_lane("vendor_runner_contract", [sys.executable, str(ROOT / "scripts" / "check_vendor_runner_template_drift.py")], env)
    _run_lane("install_python", [str(ROOT / "scripts" / "ci" / "install_python.sh")], env)
    repo_env = dict(env)
    repo_env["HLA2010_SKIP_TARGET_RADAR_BACKEND_MATRIX"] = "1"
    _run_lane("repo_green", [sys.executable, str(ROOT / "scripts" / "ci" / "repo_green.py")], repo_env)
    _run_lane("seed_suite", ["env", "HLA2010_SKIP_TARGET_RADAR_BACKEND_MATRIX=1", str(ROOT / "scripts" / "ci" / "seed_suite.sh")], env)
    _run_lane("optional_java_bridges", [sys.executable, str(ROOT / "scripts" / "ci" / "test.py"), "tests/runtime/test_optional_real_java_bridges.py"], env)
    _run_lane("target_radar_backend_matrix", [str(ROOT / "scripts" / "ci" / "target_radar_backend_matrix.sh")], env)
    _run_lane("target_radar_proof", [str(ROOT / "scripts" / "ci" / "target_radar_proof.sh")], env)


def _run_required_vendor_lane(name: str, profile: str, env: dict[str, str]) -> None:
    override_var = f"HLA2010_GITHUB_CI_LOCAL_{name.upper().replace('-', '_')}_CMD"
    _log(name)
    override = env.get(override_var)
    if override:
        result = subprocess.run(["bash", "-lc", override], cwd=ROOT, env=env, check=False)
        if result.returncode != 0:
            raise SystemExit(result.returncode)
        return
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ci" / "check_vendor_runtime_ci_state.py"), "--profile", profile],
        cwd=ROOT,
        env=env,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ci" / "vendor_green.py"), profile],
        cwd=ROOT,
        env=env,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def _run_vendor_required(env: dict[str, str]) -> None:
    _run_lane("install_python", [str(ROOT / "scripts" / "ci" / "install_python.sh")], env)
    _run_required_vendor_lane("certi_runtime_required", "certi", env)
    _run_required_vendor_lane("pitch_runtime_required", "pitch", env)
    _run_required_vendor_lane("real_profile_matrix_required", "matrix", env)


def _run_vendor_edge(env: dict[str, str]) -> None:
    _run_lane("install_python", [str(ROOT / "scripts" / "ci" / "install_python.sh")], env)
    _run_lane("vendor_edge_matrix_validate", [sys.executable, str(ROOT / "scripts" / "ci" / "check_vendor_runtime_ci_state.py"), "--profile", "vendor-edge"], env)
    for profile in ("time-query", "negotiated-ownership", "save-restore", "ddm"):
        _run_lane(f"vendor_edge_{profile}", [sys.executable, str(ROOT / "scripts" / "ci" / "vendor_edge_matrix.py"), profile], env)


def _run_probe_review(env: dict[str, str]) -> None:
    _run_lane("install_python", [str(ROOT / "scripts" / "ci" / "install_python.sh")], env)
    _run_lane("vendor_probe_review_validate", [sys.executable, str(ROOT / "scripts" / "ci" / "check_vendor_runtime_ci_state.py"), "--profile", "vendor-edge"], env)
    for profile in (
        "certi-save-restore-probe",
        "certi-ddm-probe",
        "pitch-save-restore-probe",
        "pitch-ddm-probe",
        "pitch-negotiated-probe",
        "pitch-time-window-probe",
        "pitch-time-window-restore-state-probe",
        "pitch-lost-federate-probe",
    ):
        _run_lane(f"probe_review_{profile}", [sys.executable, str(ROOT / "scripts" / "ci" / "run_vendor_probe_review.py"), profile, "5"], env)


def _run_vendor_smoke(env: dict[str, str]) -> None:
    _run_lane("install_python", [str(ROOT / "scripts" / "ci" / "install_python.sh")], env)
    entries = [
        ("all", "all", [sys.executable, str(ROOT / "scripts" / "ci" / "vendor_green.py"), "all"]),
        ("certi-save-restore-probe", "certi", [str(ROOT / "tools" / "certi-easy"), "save-restore-probe"]),
        ("certi-ddm-probe", "certi", [str(ROOT / "tools" / "certi-easy"), "ddm-probe"]),
        ("pitch-save-restore-probe", "pitch", [str(ROOT / "tools" / "pitch"), "save-restore-probe"]),
        ("pitch-ddm-probe", "pitch", [str(ROOT / "tools" / "pitch"), "ddm-probe"]),
        ("pitch-negotiated-probe", "pitch", [str(ROOT / "tools" / "pitch"), "negotiated-probe"]),
        ("pitch-time-window-probe", "pitch", [str(ROOT / "tools" / "pitch"), "time-window-probe"]),
        ("pitch-time-window-restore-state-probe", "pitch", [str(ROOT / "tools" / "pitch"), "time-window-restore-state-probe"]),
        ("pitch-lost-federate-probe", "pitch", [str(ROOT / "tools" / "pitch"), "lost-federate-probe"]),
    ]
    for name, profile, command in entries:
        _run_lane(f"vendor_smoke_validate_{name}", [sys.executable, str(ROOT / "scripts" / "ci" / "check_vendor_runtime_ci_state.py"), "--profile", profile], env)
        _run_lane(f"vendor_smoke_{name}", command, env)


def main(argv: list[str]) -> int:
    args = argv[1:]
    if args and args[0] in {"help", "-h", "--help"}:
        print(_usage())
        return 0
    mode = args[0] if args else "default"
    if mode not in VALID_MODES:
        print(_usage(), file=sys.stderr)
        return 2
    env = os.environ.copy()
    if mode == "default":
        _run_default(env)
    elif mode == "vendor-required":
        _run_vendor_required(env)
    elif mode == "vendor-edge":
        _run_vendor_edge(env)
    elif mode == "probe-review":
        _run_probe_review(env)
    elif mode == "vendor-smoke":
        _run_vendor_smoke(env)
    elif mode == "all":
        _run_default(env)
        _run_vendor_required(env)
        _run_vendor_edge(env)
        _run_probe_review(env)
        _run_vendor_smoke(env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
