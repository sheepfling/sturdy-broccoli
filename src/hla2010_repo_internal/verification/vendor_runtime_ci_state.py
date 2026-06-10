"""Dedicated CI runtime-state validation for vendor-green jobs."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VendorRuntimeCiStatePaths:
    output_dir: Path
    summary_json: Path
    report_markdown: Path


_PROFILE_SPECS: dict[str, dict[str, Any]] = {
    "certi": {
        "required_vars": (
            "HLA2010_CERTI_PATCHED_PREFIX",
            "HLA2010_CERTI_PATCHED_BUILD_ROOT",
        ),
        "compatibility_vars": {
            "HLA2010_CERTI_PREFIX": "HLA2010_CERTI_PATCHED_PREFIX",
            "HLA2010_CERTI_BUILD_ROOT": "HLA2010_CERTI_PATCHED_BUILD_ROOT",
        },
        "required_markers": (
            "${HLA2010_CERTI_PATCHED_PREFIX}/bin/rtig",
            "${HLA2010_CERTI_PATCHED_BUILD_ROOT}/libRTI/ieee1516-2010",
        ),
    },
    "pitch": {
        "required_vars": (
            "HLA2010_PITCH_HOME",
            "HLA2010_PITCH_USER_HOME",
        ),
        "compatibility_vars": {},
        "required_markers": (
            "${HLA2010_PITCH_HOME}/lib/prtifull.jar",
        ),
    },
    "matrix": {
        "required_vars": (
            "HLA2010_CERTI_PATCHED_PREFIX",
            "HLA2010_CERTI_PATCHED_BUILD_ROOT",
            "HLA2010_CERTI_UPSTREAM_PREFIX",
            "HLA2010_CERTI_UPSTREAM_BUILD_ROOT",
            "HLA2010_PITCH_HOME",
            "HLA2010_PITCH_USER_HOME",
        ),
        "compatibility_vars": {
            "HLA2010_CERTI_PREFIX": "HLA2010_CERTI_PATCHED_PREFIX",
            "HLA2010_CERTI_BUILD_ROOT": "HLA2010_CERTI_PATCHED_BUILD_ROOT",
        },
        "required_markers": (
            "${HLA2010_CERTI_PATCHED_PREFIX}/bin/rtig",
            "${HLA2010_CERTI_PATCHED_BUILD_ROOT}/libRTI/ieee1516-2010",
            "${HLA2010_CERTI_UPSTREAM_PREFIX}/bin/rtig",
            "${HLA2010_CERTI_UPSTREAM_BUILD_ROOT}/libRTI/ieee1516-2010",
            "${HLA2010_PITCH_HOME}/lib/prtifull.jar",
        ),
    },
    "vendor-edge": {
        "required_vars": (
            "HLA2010_CERTI_PATCHED_PREFIX",
            "HLA2010_CERTI_PATCHED_BUILD_ROOT",
            "HLA2010_CERTI_UPSTREAM_PREFIX",
            "HLA2010_CERTI_UPSTREAM_BUILD_ROOT",
            "HLA2010_PITCH_HOME",
            "HLA2010_PITCH_USER_HOME",
        ),
        "compatibility_vars": {
            "HLA2010_CERTI_PREFIX": "HLA2010_CERTI_PATCHED_PREFIX",
            "HLA2010_CERTI_BUILD_ROOT": "HLA2010_CERTI_PATCHED_BUILD_ROOT",
        },
        "required_markers": (
            "${HLA2010_CERTI_PATCHED_PREFIX}/bin/rtig",
            "${HLA2010_CERTI_PATCHED_BUILD_ROOT}/libRTI/ieee1516-2010",
            "${HLA2010_CERTI_UPSTREAM_PREFIX}/bin/rtig",
            "${HLA2010_CERTI_UPSTREAM_BUILD_ROOT}/libRTI/ieee1516-2010",
            "${HLA2010_PITCH_HOME}/lib/prtifull.jar",
        ),
    },
    "all": {
        "required_vars": (
            "HLA2010_CERTI_PATCHED_PREFIX",
            "HLA2010_CERTI_PATCHED_BUILD_ROOT",
            "HLA2010_PITCH_HOME",
            "HLA2010_PITCH_USER_HOME",
        ),
        "compatibility_vars": {
            "HLA2010_CERTI_PREFIX": "HLA2010_CERTI_PATCHED_PREFIX",
            "HLA2010_CERTI_BUILD_ROOT": "HLA2010_CERTI_PATCHED_BUILD_ROOT",
        },
        "required_markers": (
            "${HLA2010_CERTI_PATCHED_PREFIX}/bin/rtig",
            "${HLA2010_CERTI_PATCHED_BUILD_ROOT}/libRTI/ieee1516-2010",
            "${HLA2010_PITCH_HOME}/lib/prtifull.jar",
        ),
    },
}


def _check_env_path(
    env_var: str,
    *,
    label: str,
    marker: str | None = None,
    require_dir: bool = False,
) -> dict[str, Any]:
    value = os.environ.get(env_var)
    if not value:
        return {
            "name": label,
            "ok": False,
            "env_var": env_var,
            "detail": f"{env_var} is not set",
        }
    path = Path(value).expanduser()
    record: dict[str, Any] = {
        "name": label,
        "ok": True,
        "env_var": env_var,
        "path": str(path),
        "detail": f"{env_var}={path}",
    }
    if require_dir and not path.is_dir():
        record["ok"] = False
        record["detail"] = f"{env_var} does not point to an existing directory: {path}"
        return record
    if marker is not None:
        marker_path = path / marker
        record["marker"] = str(marker_path)
        if not marker_path.exists():
            record["ok"] = False
            record["detail"] = f"{env_var} is missing required marker {marker_path}"
    return record


def _check_pitch_user_home() -> dict[str, Any]:
    value = os.environ.get("HLA2010_PITCH_USER_HOME")
    if not value:
        return {
            "name": "pitch-user-home",
            "ok": False,
            "env_var": "HLA2010_PITCH_USER_HOME",
            "detail": "HLA2010_PITCH_USER_HOME is not set",
        }
    path = Path(value).expanduser()
    parent = path.parent
    ok = parent.exists()
    detail = f"HLA2010_PITCH_USER_HOME={path}"
    if not ok:
        detail = f"HLA2010_PITCH_USER_HOME parent directory does not exist: {parent}"
    return {
        "name": "pitch-user-home",
        "ok": ok,
        "env_var": "HLA2010_PITCH_USER_HOME",
        "path": str(path),
        "detail": detail,
    }


def vendor_runtime_ci_profile_spec(profile: str) -> dict[str, Any]:
    try:
        spec = _PROFILE_SPECS[profile]
    except KeyError as exc:
        raise ValueError(f"unsupported CI runtime-state profile: {profile}") from exc
    return {
        "required_vars": tuple(spec["required_vars"]),
        "compatibility_vars": dict(spec["compatibility_vars"]),
        "required_markers": tuple(spec["required_markers"]),
    }


def vendor_runtime_ci_profiles() -> tuple[str, ...]:
    return tuple(_PROFILE_SPECS)


def _profile_checks(profile: str) -> tuple[dict[str, Any], ...]:
    certi_patched = (
        _check_env_path(
            "HLA2010_CERTI_PATCHED_PREFIX",
            label="certi-patched-prefix",
            marker="bin/rtig",
            require_dir=True,
        ),
        _check_env_path(
            "HLA2010_CERTI_PATCHED_BUILD_ROOT",
            label="certi-patched-build-root",
            marker="libRTI/ieee1516-2010",
            require_dir=True,
        ),
    )
    certi_upstream = (
        _check_env_path(
            "HLA2010_CERTI_UPSTREAM_PREFIX",
            label="certi-upstream-prefix",
            marker="bin/rtig",
            require_dir=True,
        ),
        _check_env_path(
            "HLA2010_CERTI_UPSTREAM_BUILD_ROOT",
            label="certi-upstream-build-root",
            marker="libRTI/ieee1516-2010",
            require_dir=True,
        ),
    )
    pitch = (
        _check_env_path(
            "HLA2010_PITCH_HOME",
            label="pitch-home",
            marker="lib/prtifull.jar",
            require_dir=True,
        ),
        _check_pitch_user_home(),
    )
    mapping = {
        "certi": certi_patched,
        "pitch": pitch,
        "matrix": certi_patched + certi_upstream + pitch,
        "vendor-edge": certi_patched + certi_upstream + pitch,
        "all": certi_patched + pitch,
    }
    if profile not in mapping:
        raise ValueError(f"unsupported CI runtime-state profile: {profile}")
    return mapping[profile]


def build_vendor_runtime_ci_state(profile: str) -> dict[str, Any]:
    spec = vendor_runtime_ci_profile_spec(profile)
    checks = list(_profile_checks(profile))
    ready = all(bool(check["ok"]) for check in checks)
    next_steps: list[str] = []
    if not ready:
        if profile in {"certi", "matrix", "vendor-edge", "all"}:
            next_steps.append("configure explicit CERTI *_PREFIX and *_BUILD_ROOT CI vars")
        if profile in {"pitch", "matrix", "vendor-edge", "all"}:
            next_steps.append("configure explicit HLA2010_PITCH_HOME and HLA2010_PITCH_USER_HOME CI vars")
    return {
        "suite_name": "vendor-runtime-ci-state",
        "profile": profile,
        "required_vars": list(spec["required_vars"]),
        "compatibility_vars": dict(spec["compatibility_vars"]),
        "required_markers": list(spec["required_markers"]),
        "classification": "ready" if ready else "invalid-runtime-state",
        "checks": checks,
        "next_steps": next_steps,
        "exit_code": 0 if ready else 1,
    }


def _write_markdown(path: Path, summary: dict[str, Any]) -> Path:
    lines = [
        "# Vendor Runtime CI State",
        "",
        f"- profile: `{summary['profile']}`",
        f"- classification: `{summary['classification']}`",
        f"- exit code: `{summary['exit_code']}`",
        "",
        "## Contract",
        "",
        f"- required vars: `{', '.join(summary['required_vars'])}`",
        f"- compatibility vars: `{', '.join(f'{k}->{v}' for k, v in summary['compatibility_vars'].items()) or '(none)'}`",
        "",
        "| Check | OK | Env Var | Detail |",
        "| --- | --- | --- | --- |",
    ]
    if summary["required_markers"]:
        lines.append("")
        lines.append("Required markers:")
        for marker in summary["required_markers"]:
            lines.append(f"- `{marker}`")
    for check in summary["checks"]:
        lines.append(
            f"| {check['name']} | {'yes' if check['ok'] else 'no'} | "
            f"{check.get('env_var', '')} | {check['detail']} |"
        )
    if summary["next_steps"]:
        lines.append("")
        lines.append("## Next Steps")
        lines.append("")
        for step in summary["next_steps"]:
            lines.append(f"- {step}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_vendor_runtime_ci_state(output_dir: Path | str, *, profile: str) -> VendorRuntimeCiStatePaths:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    paths = VendorRuntimeCiStatePaths(
        output_dir=output_path,
        summary_json=output_path / "vendor_runtime_ci_state_summary.json",
        report_markdown=output_path / "vendor_runtime_ci_state_report.md",
    )
    summary = build_vendor_runtime_ci_state(profile)
    paths.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(paths.report_markdown, summary)
    return paths


__all__ = [
    "VendorRuntimeCiStatePaths",
    "build_vendor_runtime_ci_state",
    "vendor_runtime_ci_profile_spec",
    "vendor_runtime_ci_profiles",
    "write_vendor_runtime_ci_state",
]
