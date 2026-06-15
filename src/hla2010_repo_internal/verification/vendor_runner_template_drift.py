"""Checks for drift between runner provisioning artifacts and executable policy."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .path_rendering import render_path
from .vendor_runtime_ci_state import vendor_runtime_ci_profile_spec, vendor_runtime_ci_profiles


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TEMPLATE_PATH = REPO_ROOT / "docs" / "vendor_runner_provisioning_template.yaml"
DEFAULT_CI_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"
DEFAULT_VENDOR_SMOKE_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "vendor-runtime-smoke.yml"

WORKFLOW_PROFILE_MAP: dict[str, tuple[Path, str]] = {
    "certi": (DEFAULT_CI_WORKFLOW_PATH, "certi-runtime-required"),
    "pitch": (DEFAULT_CI_WORKFLOW_PATH, "pitch-runtime-required"),
    "matrix": (DEFAULT_CI_WORKFLOW_PATH, "real-profile-matrix-required"),
    "vendor-edge": (DEFAULT_CI_WORKFLOW_PATH, "vendor-edge-matrix-required"),
    "all": (DEFAULT_VENDOR_SMOKE_WORKFLOW_PATH, "vendor-runtime-smoke"),
}


@dataclass(frozen=True)
class VendorRunnerTemplateDriftPaths:
    output_dir: Path
    summary_json: Path
    report_markdown: Path


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _job_env(path: Path, job_name: str) -> dict[str, str]:
    payload = _load_yaml(path)
    jobs = payload.get("jobs") or {}
    job = jobs.get(job_name) or {}
    env = job.get("env") or {}
    return {str(key): str(value) for key, value in env.items()}


def _resolve_template_profile(profiles: dict[str, Any], profile_name: str) -> dict[str, Any] | None:
    profile = profiles.get(profile_name)
    if profile is None:
        return None
    parent_name = profile.get("extends")
    if parent_name is None:
        return {
            "required_vars": list(profile.get("required_vars") or []),
            "compatibility_vars": dict(profile.get("compatibility_vars") or {}),
            "required_markers": list(profile.get("required_markers") or []),
        }
    parent = _resolve_template_profile(profiles, str(parent_name))
    if parent is None:
        return None
    return {
        "required_vars": list(profile.get("required_vars") or parent["required_vars"]),
        "compatibility_vars": dict(profile.get("compatibility_vars") or parent["compatibility_vars"]),
        "required_markers": list(profile.get("required_markers") or parent["required_markers"]),
    }


def build_vendor_runner_template_drift(
    template_path: Path | str = DEFAULT_TEMPLATE_PATH,
) -> dict[str, Any]:
    template = _load_yaml(Path(template_path))
    template_profiles = template.get("profiles") or {}
    expected_profiles = vendor_runtime_ci_profiles()

    rows: list[dict[str, Any]] = []
    for profile in expected_profiles:
        spec = vendor_runtime_ci_profile_spec(profile)
        template_profile = _resolve_template_profile(template_profiles, profile)
        if template_profile is None:
            rows.append(
                {
                    "profile": profile,
                    "ok": False,
                    "reason": "missing-template-profile",
                }
            )
            continue
        expected_required_vars = list(spec["required_vars"])
        expected_compatibility_vars = spec["compatibility_vars"]
        expected_required_markers = list(spec["required_markers"])
        workflow_path, job_name = WORKFLOW_PROFILE_MAP[profile]
        env = _job_env(workflow_path, job_name)
        missing_workflow_vars = [name for name in expected_required_vars if name not in env]
        missing_compatibility_vars = [name for name in expected_compatibility_vars if name not in env]
        ok = (
            list(template_profile["required_vars"]) == expected_required_vars
            and dict(template_profile["compatibility_vars"]) == expected_compatibility_vars
            and list(template_profile["required_markers"]) == expected_required_markers
            and not missing_workflow_vars
            and not missing_compatibility_vars
        )
        rows.append(
            {
                "profile": profile,
                "ok": ok,
                "reason": "ok" if ok else "template-or-workflow-drift",
                "expected_required_vars": expected_required_vars,
                "template_required_vars": list(template_profile["required_vars"]),
                "expected_compatibility_vars": expected_compatibility_vars,
                "template_compatibility_vars": dict(template_profile["compatibility_vars"]),
                "expected_required_markers": expected_required_markers,
                "template_required_markers": list(template_profile["required_markers"]),
                "workflow": str(workflow_path.relative_to(REPO_ROOT)),
                "job_name": job_name,
                "missing_workflow_vars": missing_workflow_vars,
                "missing_compatibility_vars": missing_compatibility_vars,
            }
        )

    overall_ok = all(bool(row["ok"]) for row in rows)
    return {
        "suite_name": "vendor-runner-template-drift",
        "template_path": render_path(Path(template_path)),
        "profiles": rows,
        "exit_code": 0 if overall_ok else 1,
    }


def _write_markdown(path: Path, summary: dict[str, Any]) -> Path:
    lines = [
        "# Vendor Runner Template Drift",
        "",
        f"- template: `{summary['template_path']}`",
        f"- exit code: `{summary['exit_code']}`",
        "",
        "| Profile | OK | Workflow Job | Reason |",
        "| --- | --- | --- | --- |",
    ]
    for row in summary["profiles"]:
        lines.append(
            f"| {row['profile']} | {'yes' if row['ok'] else 'no'} | "
            f"{row.get('workflow', '')}:{row.get('job_name', '')} | {row['reason']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_vendor_runner_template_drift(
    output_dir: Path | str,
    *,
    template_path: Path | str = DEFAULT_TEMPLATE_PATH,
) -> VendorRunnerTemplateDriftPaths:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    paths = VendorRunnerTemplateDriftPaths(
        output_dir=output_path,
        summary_json=output_path / "vendor_runner_template_drift_summary.json",
        report_markdown=output_path / "vendor_runner_template_drift_report.md",
    )
    summary = build_vendor_runner_template_drift(template_path=template_path)
    paths.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(paths.report_markdown, summary)
    return paths


__all__ = [
    "VendorRunnerTemplateDriftPaths",
    "build_vendor_runner_template_drift",
    "write_vendor_runner_template_drift",
]
