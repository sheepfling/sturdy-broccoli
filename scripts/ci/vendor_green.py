#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def ci_state_profile(profile: str) -> str:
    if profile in {"certi", "certi-patched", "certi-upstream", "certi-compare", "certi-save-restore", "certi-save-restore-probe", "certi-ddm", "certi-ddm-probe"}:
        return "certi"
    if profile in {"pitch", "pitch-smoke", "pitch-verify", "pitch-save-restore", "pitch-save-restore-probe", "pitch-ddm", "pitch-ddm-probe", "pitch-negotiated", "pitch-negotiated-probe", "pitch-time-window-probe", "pitch-time-window-restore-state-probe", "pitch-lost-federate", "pitch-lost-federate-probe"}:
        return "pitch"
    if profile in {"matrix", "vendor-edge"}:
        return profile
    return "all"


def should_validate_ci_state(setting: str) -> bool:
    normalized = setting.strip().lower()
    if normalized in {"1", "true", "yes", "always"}:
        return True
    if normalized in {"0", "false", "no", "never"}:
        return False
    if normalized == "auto":
        return os.environ.get("GITHUB_ACTIONS") == "true"
    raise SystemExit(f"unsupported HLA2010_VENDOR_GREEN_REQUIRE_CI_STATE value: {setting}")


def _usage() -> str:
    return "\n".join(
        [
            "usage: ./scripts/ci/vendor_green.py [profile]",
            "",
            "Run the strict vendor-green lane.",
            "",
            "- delegates to ./scripts/ci/vendor_runtime_smoke.py",
            "- forces HLA2010_VENDOR_PREFLIGHT_STRICT=1",
            "- validates dedicated runner runtime-state before execution when running under CI",
            "- fails immediately when CERTI or Pitch prerequisites are blocked",
            "- always emits normalized vendor runtime status and parity artifacts on exit",
            "",
            "Pitch profiles:",
            "- pitch-smoke",
            "- pitch-verify",
            "- pitch-save-restore",
            "- pitch-save-restore-probe",
            "- pitch-ddm",
            "- pitch-ddm-probe",
            "- pitch-negotiated",
            "- pitch-negotiated-probe",
            "- pitch-time-window-probe",
            "- pitch-time-window-restore-state-probe",
            "- pitch-lost-federate",
            "- pitch-lost-federate-probe",
            "- pitch",
            "",
            "CERTI profiles:",
            "- certi-save-restore",
            "- certi-save-restore-probe",
            "- certi-ddm",
            "- certi-ddm-probe",
            "",
            "Use ./scripts/ci/repo_green.py for the repo-green lane.",
        ]
    )


def main(argv: list[str]) -> int:
    args = argv[1:]
    if args and args[0] in {"-h", "--help", "help"}:
        print(_usage())
        return 0

    profile = args[0] if args else "matrix"
    delegate = os.environ.get("HLA2010_VENDOR_GREEN_DELEGATE", str(ROOT / "scripts" / "ci" / "vendor_runtime_smoke.py"))
    ci_state_output_dir = os.environ.get("HLA2010_VENDOR_RUNTIME_CI_STATE_DIR", str(ROOT / "artifacts" / "vendor_runtime_ci_state"))
    ci_state_required = os.environ.get("HLA2010_VENDOR_GREEN_REQUIRE_CI_STATE", "auto")
    env = os.environ.copy()
    env["HLA2010_VENDOR_PREFLIGHT_STRICT"] = "1"

    status = 0
    if should_validate_ci_state(ci_state_required):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "ci" / "check_vendor_runtime_ci_state.py"),
                "--profile",
                ci_state_profile(profile),
                "--output-dir",
                ci_state_output_dir,
            ],
            cwd=ROOT,
            env=env,
            check=False,
        )
        if result.returncode != 0:
            subprocess.run([str(ROOT / "scripts" / "ci" / "emit_vendor_runtime_reports.sh"), "vendor-green", profile], cwd=ROOT, env=env, check=False)
            return result.returncode

    delegate_argv = [sys.executable, delegate, profile] if Path(delegate).suffix == ".py" else [delegate, profile]
    result = subprocess.run(delegate_argv, cwd=ROOT, env=env, check=False)
    status = result.returncode
    subprocess.run([str(ROOT / "scripts" / "ci" / "emit_vendor_runtime_reports.sh"), "vendor-green", profile], cwd=ROOT, env=env, check=False)
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
