"""Vendor parity artifact manifest writer."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .vendor_gap_profiles import get_vendor_gap_profile
from .vendor_runtime_status import build_vendor_runtime_status


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "analysis").exists() and (parent / "tools").exists():
            return parent
    raise RuntimeError("Could not locate repository root")


REPO_ROOT = _repo_root()


@dataclass(frozen=True)
class VendorParityArtifactPaths:
    output_dir: Path
    summary_json: Path
    artifact_manifest_csv: Path
    report_markdown: Path


@dataclass(frozen=True)
class VendorParityArtifactRow:
    vendor_family: str
    profile: str
    evidence_tier: str
    artifact_kind: str
    role: str
    path: str
    required: bool
    exists: bool
    note: str


_ARTIFACT_SPECS: tuple[dict[str, Any], ...] = (
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "script",
        "role": "runtime smoke entrypoint",
        "path": "scripts/ci/vendor_runtime_smoke.sh",
        "required": True,
        "note": "Main real-runtime smoke/profile runner for CERTI and Pitch.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "script",
        "role": "edge matrix operator wrapper",
        "path": "tools/vendor-edge",
        "required": True,
        "note": "Highest-value vendor edge slice wrapper.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "test",
        "role": "smoke test",
        "path": "tests/vendors/test_real_vendor_runtime_smoke.py",
        "required": True,
        "note": "Backend-neutral real vendor runtime smoke anchor.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "doc",
        "role": "parity matrix",
        "path": "docs/backend_conformance_matrix.md",
        "required": True,
        "note": "Clause-level parity and vendor status summary.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "doc",
        "role": "runtime options matrix",
        "path": "docs/rti_options_and_test_matrix.md",
        "required": True,
        "note": "Supported vendor/runtime families and route inventory.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "script",
        "role": "preflight classifier wrapper",
        "path": "tools/vendor-state",
        "required": True,
        "note": "Machine-readable readiness classifier over vendor preflight artifacts.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "script",
        "role": "probe stability entrypoint",
        "path": "scripts/ci/vendor_probe_stability.sh",
        "required": True,
        "note": "Repeated-run stability harness for dedicated vendor probe profiles.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "script",
        "role": "promotion review operator wrapper",
        "path": "tools/vendor-probe-review",
        "required": True,
        "note": "Promotion-review artifact writer over repeated-run vendor probe evidence.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "preflight",
        "role": "preflight snapshot",
        "path": "analysis/preflight_artifacts/certi-preflight.json",
        "required": False,
        "note": "Optional machine-readable CERTI environment snapshot.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "preflight",
        "role": "preflight snapshot",
        "path": "analysis/preflight_artifacts/pitch-preflight.json",
        "required": False,
        "note": "Optional machine-readable Pitch environment snapshot.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-save-restore-probe",
        "artifact_kind": "stability-summary",
        "role": "probe stability summary",
        "path": "analysis/vendor_probe_stability/certi-save-restore-probe/vendor_probe_stability_summary.json",
        "required": False,
        "note": "Optional repeated-run stability summary for the CERTI save/restore probe.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-ddm-probe",
        "artifact_kind": "stability-summary",
        "role": "probe stability summary",
        "path": "analysis/vendor_probe_stability/certi-ddm-probe/vendor_probe_stability_summary.json",
        "required": False,
        "note": "Optional repeated-run stability summary for the CERTI DDM probe.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-save-restore-probe",
        "artifact_kind": "stability-summary",
        "role": "probe stability summary",
        "path": "analysis/vendor_probe_stability/pitch-save-restore-probe/vendor_probe_stability_summary.json",
        "required": False,
        "note": "Optional repeated-run stability summary for the Pitch save/restore probe.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-ddm-probe",
        "artifact_kind": "stability-summary",
        "role": "probe stability summary",
        "path": "analysis/vendor_probe_stability/pitch-ddm-probe/vendor_probe_stability_summary.json",
        "required": False,
        "note": "Optional repeated-run stability summary for the Pitch DDM probe.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-negotiated-probe",
        "artifact_kind": "stability-summary",
        "role": "probe stability summary",
        "path": "analysis/vendor_probe_stability/pitch-negotiated-probe/vendor_probe_stability_summary.json",
        "required": False,
        "note": "Optional repeated-run stability summary for the Pitch negotiated-ownership probe.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-lost-federate-probe",
        "artifact_kind": "stability-summary",
        "role": "probe stability summary",
        "path": "analysis/vendor_probe_stability/pitch-lost-federate-probe/vendor_probe_stability_summary.json",
        "required": False,
        "note": "Optional repeated-run stability summary for the Pitch lost-federate probe.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "artifact_kind": "promotion-review",
        "role": "probe promotion review summary",
        "path": "analysis/vendor_probe_promotion_review/vendor_probe_promotion_review_summary.json",
        "required": False,
        "note": "Optional promotion-review summary comparing repeated-run probe evidence against documented conformance stance.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-save-restore",
        "artifact_kind": "gap-profile",
        "role": "known gap profile",
        "path": "analysis/vendor_gap_profiles/certi-save-restore.json",
        "required": False,
        "note": "Optional machine-readable CERTI save/restore known-gap profile.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-ddm",
        "artifact_kind": "gap-profile",
        "role": "known gap profile",
        "path": "analysis/vendor_gap_profiles/certi-ddm.json",
        "required": False,
        "note": "Optional machine-readable CERTI DDM known-gap profile.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-save-restore",
        "artifact_kind": "gap-profile",
        "role": "known gap profile",
        "path": "analysis/vendor_gap_profiles/pitch-save-restore.json",
        "required": False,
        "note": "Optional machine-readable Pitch save/restore known-gap profile.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-ddm",
        "artifact_kind": "gap-profile",
        "role": "known gap profile",
        "path": "analysis/vendor_gap_profiles/pitch-ddm.json",
        "required": False,
        "note": "Optional machine-readable Pitch DDM known-gap profile.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-negotiated",
        "artifact_kind": "gap-profile",
        "role": "known gap profile",
        "path": "analysis/vendor_gap_profiles/pitch-negotiated.json",
        "required": False,
        "note": "Optional machine-readable Pitch negotiated-ownership known-gap profile.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-lost-federate",
        "artifact_kind": "gap-profile",
        "role": "known gap profile",
        "path": "analysis/vendor_gap_profiles/pitch-lost-federate.json",
        "required": False,
        "note": "Optional machine-readable Pitch lost-federate known-gap profile.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "artifact_kind": "test",
        "role": "exchange parity",
        "path": "tests/vendors/test_certi_real_backend_exchange_matrix.py",
        "required": True,
        "note": "Real CERTI exchange scenario parity slice.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "artifact_kind": "test",
        "role": "time parity",
        "path": "tests/vendors/test_certi_real_backend_time_matrix.py",
        "required": True,
        "note": "Real CERTI time-management compare slice.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "artifact_kind": "test",
        "role": "ownership parity",
        "path": "tests/vendors/test_certi_real_backend_ownership_matrix.py",
        "required": True,
        "note": "Real CERTI ownership compare slice.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "artifact_kind": "support",
        "role": "shared matrix helpers",
        "path": "tests/vendors/certi_real_backend_matrix_support.py",
        "required": True,
        "note": "Shared CERTI runtime guards and helpers.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "artifact_kind": "doc",
        "role": "runbook",
        "path": "packages/hla-backend-certi/docs/certi_section8_runbook.md",
        "required": True,
        "note": "Operational runbook for CERTI compare workflows.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "artifact_kind": "doc",
        "role": "traceability note",
        "path": "packages/hla-backend-certi/docs/certi_spec_traceability.md",
        "required": True,
        "note": "Clause-level CERTI evidence and traceability context.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "artifact_kind": "doc",
        "role": "vendor findings",
        "path": "packages/hla-backend-certi/docs/certi_negotiated_ownership_findings.md",
        "required": True,
        "note": "Current negotiated ownership divergence notes for CERTI.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch",
        "artifact_kind": "test",
        "role": "exchange time ownership parity",
        "path": "tests/vendors/test_pitch_real_backend_matrix.py",
        "required": True,
        "note": "Real Pitch backend matrix across exchange, time, sync, and ownership slices.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch",
        "artifact_kind": "doc",
        "role": "quickstart",
        "path": "packages/hla-vendor-pitch/docs/pitch_docker_quickstart.md",
        "required": True,
        "note": "Shortest supported Pitch runtime activation path.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch",
        "artifact_kind": "doc",
        "role": "decision tree",
        "path": "packages/hla-vendor-pitch/docs/pitch_decision_tree.md",
        "required": True,
        "note": "Pitch operator decision tree and environment branching.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch",
        "artifact_kind": "doc",
        "role": "vendor findings",
        "path": "packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",
        "required": True,
        "note": "Current negotiated ownership divergence notes for Pitch.",
    },
)

_PROFILE_COMMANDS: tuple[dict[str, str], ...] = (
    {
        "vendor_family": "certi",
        "profile": "certi-compare",
        "command": "./tools/certi-easy smoke compare",
        "purpose": "Run the current upstream-vs-patched CERTI compare slice.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch",
        "command": "./tools/pitch smoke",
        "purpose": "Run the current Pitch runtime smoke and matrix slice.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "command": "./tools/vendor-state classify --lane repo-green --json",
        "purpose": "Classify whether blocked vendor prerequisites are acceptable for the repo-green lane.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "command": "./tools/vendor-state classify --lane vendor-green --vendor certi --json",
        "purpose": "Classify strict CERTI vendor-green readiness from preflight artifacts.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "command": "./tools/vendor-state classify --lane vendor-green --vendor pitch --json",
        "purpose": "Classify strict Pitch vendor-green readiness from preflight artifacts.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-save-restore",
        "command": "./tools/certi-easy save-restore",
        "purpose": "Emit the current explicit CERTI save/restore known-gap status after preflight.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-save-restore-probe",
        "command": "./tools/certi-easy save-restore-probe",
        "purpose": "Run the current narrow executable CERTI save/restore runtime probe after preflight.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-ddm",
        "command": "./tools/certi-easy ddm",
        "purpose": "Emit the current explicit CERTI DDM known-gap status after preflight.",
    },
    {
        "vendor_family": "certi",
        "profile": "certi-ddm-probe",
        "command": "./tools/certi-easy ddm-probe",
        "purpose": "Run the current narrow executable CERTI DDM runtime probe after preflight.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-save-restore",
        "command": "./tools/pitch save-restore",
        "purpose": "Emit the current explicit Pitch save/restore known-gap status after preflight.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-save-restore-probe",
        "command": "./tools/pitch save-restore-probe",
        "purpose": "Run the current narrow executable Pitch save/restore runtime probe after preflight.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-ddm",
        "command": "./tools/pitch ddm",
        "purpose": "Emit the current explicit Pitch DDM known-gap status after preflight.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-ddm-probe",
        "command": "./tools/pitch ddm-probe",
        "purpose": "Run the current narrow executable Pitch DDM runtime probe after preflight.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-negotiated",
        "command": "./tools/pitch negotiated",
        "purpose": "Emit the current explicit Pitch negotiated-ownership known-gap status after preflight.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-negotiated-probe",
        "command": "./tools/pitch negotiated-probe",
        "purpose": "Run the current narrow executable Pitch negotiated-ownership runtime probe after preflight.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-lost-federate",
        "command": "./tools/pitch lost-federate",
        "purpose": "Emit the current explicit Pitch lost-federate known-gap status after preflight.",
    },
    {
        "vendor_family": "pitch",
        "profile": "pitch-lost-federate-probe",
        "command": "./tools/pitch lost-federate-probe",
        "purpose": "Run the current narrow executable Pitch lost-federate runtime probe after preflight.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "command": "./tools/vendor-edge all",
        "purpose": "Run the highest-value vendor edge packet refresh.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "command": "./tools/certi-easy save-restore-review 5",
        "purpose": "Run repeated stability evidence plus promotion/parity refresh for the CERTI save/restore probe.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "command": "./tools/certi-easy ddm-review 5",
        "purpose": "Run repeated stability evidence plus promotion/parity refresh for the CERTI DDM probe.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "command": "./tools/pitch save-restore-review 5",
        "purpose": "Run repeated stability evidence plus promotion/parity refresh for the Pitch save/restore probe.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "command": "./tools/pitch ddm-review 5",
        "purpose": "Run repeated stability evidence plus promotion/parity refresh for the Pitch DDM probe.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "command": "./tools/pitch negotiated-review 5",
        "purpose": "Run repeated stability evidence plus promotion/parity refresh for the Pitch negotiated-ownership probe.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "command": "./tools/pitch lost-federate-review 5",
        "purpose": "Run repeated stability evidence plus promotion/parity refresh for the Pitch lost-federate probe.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "command": "./tools/vendor-probe-review promotion-review",
        "purpose": "Write the promotion-review artifact over repeated-run vendor probe evidence.",
    },
    {
        "vendor_family": "shared",
        "profile": "shared",
        "command": "python3 scripts/generate_compliance_artifacts.py",
        "purpose": "Refresh generated compliance matrices after a vendor run.",
    },
)


def _profile_evidence_tier(profile: str) -> str:
    if profile == "shared":
        return "shared"
    if profile.endswith("-probe"):
        return "probe"
    if profile in {
        "certi-save-restore",
        "certi-ddm",
        "pitch-save-restore",
        "pitch-ddm",
        "pitch-negotiated",
        "pitch-lost-federate",
    }:
        return "known-gap"
    if profile in {
        "certi",
        "certi-patched",
        "certi-upstream",
        "certi-compare",
        "pitch",
        "pitch-smoke",
        "pitch-verify",
        "matrix",
        "all",
    }:
        return "promoted"
    return "other"


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(getattr(value, key)) for key in value.__dataclass_fields__}
    return repr(value)


def _build_rows() -> tuple[VendorParityArtifactRow, ...]:
    rows: list[VendorParityArtifactRow] = []
    for spec in _ARTIFACT_SPECS:
        path = REPO_ROOT / spec["path"]
        rows.append(
            VendorParityArtifactRow(
                vendor_family=spec["vendor_family"],
                profile=spec["profile"],
                evidence_tier=_profile_evidence_tier(spec["profile"]),
                artifact_kind=spec["artifact_kind"],
                role=spec["role"],
                path=spec["path"],
                required=bool(spec["required"]),
                exists=path.exists(),
                note=spec["note"],
            )
        )
    return tuple(rows)


def _load_preflight_snapshot(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "tool": data.get("tool"),
        "result": data.get("result"),
        "environment": data.get("environment"),
        "exit_code": data.get("exit_code"),
    }


def _load_gap_profile(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    profile_name = data.get("profile")
    defaults = None
    if isinstance(profile_name, str):
        try:
            defaults = get_vendor_gap_profile(profile_name)
        except ValueError:
            defaults = None
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "profile": data.get("profile") or (None if defaults is None else defaults.profile),
        "vendor": data.get("vendor") or (None if defaults is None else defaults.vendor),
        "area": data.get("area") or (None if defaults is None else defaults.area),
        "classification": data.get("classification") or (None if defaults is None else defaults.classification),
        "status": data.get("status") or (None if defaults is None else defaults.status),
        "docs_ref": data.get("docs_ref") or (None if defaults is None else defaults.docs_ref),
        "recommended_operator_route": data.get("recommended_operator_route")
        or (None if defaults is None else defaults.recommended_operator_route),
        "next_steps": data.get("next_steps") or ([] if defaults is None else list(defaults.next_steps)),
        "operator_state": data.get("operator_state") or (None if defaults is None else defaults.operator_state),
        "blocker_summary": data.get("blocker_summary") or (None if defaults is None else defaults.blocker_summary),
        "operator_artifact_refs": data.get("operator_artifact_refs")
        or ([] if defaults is None else list(defaults.operator_artifact_refs)),
    }


def _load_probe_stability_summary(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "profile": data.get("profile"),
        "evidence_tier": data.get("evidence_tier"),
        "repeat_count": data.get("repeat_count"),
        "attempt_count": data.get("attempt_count"),
        "success_count": data.get("success_count"),
        "failure_count": data.get("failure_count"),
        "stable": data.get("stable"),
        "promotion_readiness": data.get("promotion_readiness"),
        "promotion_note": data.get("promotion_note"),
    }


def _load_probe_promotion_review(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "candidate_count": data.get("candidate_count"),
        "profiles": data.get("profiles"),
    }


def _build_summary(rows: tuple[VendorParityArtifactRow, ...]) -> dict[str, Any]:
    profiles: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = f"{row.vendor_family}:{row.profile}"
        entry = profiles.setdefault(
            key,
            {
                "vendor_family": row.vendor_family,
                "profile": row.profile,
                "evidence_tier": row.evidence_tier,
                "artifact_count": 0,
                "existing_count": 0,
                "missing_required_count": 0,
                "artifact_kinds": [],
            },
        )
        entry["artifact_count"] += 1
        if row.exists:
            entry["existing_count"] += 1
        if row.required and not row.exists:
            entry["missing_required_count"] += 1
        if row.artifact_kind not in entry["artifact_kinds"]:
            entry["artifact_kinds"].append(row.artifact_kind)

    preflight_dir = REPO_ROOT / "analysis" / "preflight_artifacts"
    preflight = {
        "certi": _load_preflight_snapshot(preflight_dir / "certi-preflight.json"),
        "pitch": _load_preflight_snapshot(preflight_dir / "pitch-preflight.json"),
    }
    runtime_status = {
        "repo_green": build_vendor_runtime_status(artifact_dir=preflight_dir, lane="repo-green"),
        "vendor_green": {
            "certi": build_vendor_runtime_status(artifact_dir=preflight_dir, lane="vendor-green", vendors=("certi",)),
            "pitch": build_vendor_runtime_status(artifact_dir=preflight_dir, lane="vendor-green", vendors=("pitch",)),
        },
    }
    gap_profile_dir = REPO_ROOT / "analysis" / "vendor_gap_profiles"
    gap_profiles = {
        "certi-save-restore": _load_gap_profile(gap_profile_dir / "certi-save-restore.json"),
        "certi-ddm": _load_gap_profile(gap_profile_dir / "certi-ddm.json"),
        "pitch-save-restore": _load_gap_profile(gap_profile_dir / "pitch-save-restore.json"),
        "pitch-ddm": _load_gap_profile(gap_profile_dir / "pitch-ddm.json"),
        "pitch-negotiated": _load_gap_profile(gap_profile_dir / "pitch-negotiated.json"),
        "pitch-lost-federate": _load_gap_profile(gap_profile_dir / "pitch-lost-federate.json"),
    }
    probe_stability_dir = REPO_ROOT / "analysis" / "vendor_probe_stability"
    probe_stability = {
        "certi-save-restore-probe": _load_probe_stability_summary(
            probe_stability_dir / "certi-save-restore-probe" / "vendor_probe_stability_summary.json"
        ),
        "certi-ddm-probe": _load_probe_stability_summary(
            probe_stability_dir / "certi-ddm-probe" / "vendor_probe_stability_summary.json"
        ),
        "pitch-save-restore-probe": _load_probe_stability_summary(
            probe_stability_dir / "pitch-save-restore-probe" / "vendor_probe_stability_summary.json"
        ),
        "pitch-ddm-probe": _load_probe_stability_summary(
            probe_stability_dir / "pitch-ddm-probe" / "vendor_probe_stability_summary.json"
        ),
        "pitch-negotiated-probe": _load_probe_stability_summary(
            probe_stability_dir / "pitch-negotiated-probe" / "vendor_probe_stability_summary.json"
        ),
        "pitch-lost-federate-probe": _load_probe_stability_summary(
            probe_stability_dir / "pitch-lost-federate-probe" / "vendor_probe_stability_summary.json"
        ),
    }
    probe_promotion_review = _load_probe_promotion_review(
        REPO_ROOT / "analysis" / "vendor_probe_promotion_review" / "vendor_probe_promotion_review_summary.json"
    )
    required_count = sum(1 for row in rows if row.required)
    existing_count = sum(1 for row in rows if row.exists)
    missing_required_count = sum(1 for row in rows if row.required and not row.exists)
    return {
        "suite_name": "vendor-parity-artifacts",
        "profiles": list(profiles.values()),
        "artifact_count": len(rows),
        "required_count": required_count,
        "existing_count": existing_count,
        "missing_required_count": missing_required_count,
        "profile_commands": [
            {
                **command,
                "evidence_tier": _profile_evidence_tier(command["profile"]),
            }
            for command in _PROFILE_COMMANDS
        ],
        "preflight": preflight,
        "runtime_status": runtime_status,
        "gap_profiles": gap_profiles,
        "probe_stability": probe_stability,
        "probe_promotion_review": probe_promotion_review,
        "artifacts": [_jsonable(row) for row in rows],
    }


def _write_manifest_csv(path: Path, rows: tuple[VendorParityArtifactRow, ...]) -> Path:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "vendor_family",
                "profile",
                "evidence_tier",
                "artifact_kind",
                "role",
                "path",
                "required",
                "exists",
                "note",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(_jsonable(row))
    return path


def _write_markdown(path: Path, summary: dict[str, Any], paths: VendorParityArtifactPaths) -> Path:
    lines = [
        "# Vendor Parity Artifacts",
        "",
        f"- suite: `{summary['suite_name']}`",
        f"- artifacts indexed: `{summary['artifact_count']}`",
        f"- required artifacts: `{summary['required_count']}`",
        f"- existing artifacts: `{summary['existing_count']}`",
        f"- missing required artifacts: `{summary['missing_required_count']}`",
        "",
        "## Profiles",
        "",
        "| Vendor | Profile | Tier | Indexed | Existing | Missing required | Kinds |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for profile in summary["profiles"]:
        kinds = ", ".join(profile["artifact_kinds"])
        lines.append(
            f"| {profile['vendor_family']} | {profile['profile']} | {profile['evidence_tier']} | {profile['artifact_count']} | "
            f"{profile['existing_count']} | {profile['missing_required_count']} | {kinds} |"
        )
    lines.extend(
        [
            "",
            "## Commands",
            "",
        ]
    )
    for command in summary["profile_commands"]:
        lines.append(f"- `{command['command']}` [{command['evidence_tier']}]")
        lines.append(f"  {command['purpose']}")
    lines.extend(
        [
            "",
            "## Preflight",
            "",
        ]
    )
    for vendor_family, snapshot in summary["preflight"].items():
        if snapshot is None:
            lines.append(f"- `{vendor_family}`: no JSON preflight snapshot is currently present")
        else:
            lines.append(
                f"- `{vendor_family}`: result `{snapshot.get('result')}`, environment `{snapshot.get('environment')}`, "
                f"exit `{snapshot.get('exit_code')}`, file `{snapshot.get('path')}`"
            )
    lines.extend(
        [
            "",
            "## Runtime Status",
            "",
            f"- repo-green: `{summary['runtime_status']['repo_green']['overall_classification']}` "
            f"(exit `{summary['runtime_status']['repo_green']['exit_code']}`)",
            f"- certi vendor-green: `{summary['runtime_status']['vendor_green']['certi']['overall_classification']}` "
            f"(exit `{summary['runtime_status']['vendor_green']['certi']['exit_code']}`)",
            f"- pitch vendor-green: `{summary['runtime_status']['vendor_green']['pitch']['overall_classification']}` "
            f"(exit `{summary['runtime_status']['vendor_green']['pitch']['exit_code']}`)",
        ]
    )
    for lane_name, lane_summary in (
        ("repo-green", summary["runtime_status"]["repo_green"]),
        ("certi vendor-green", summary["runtime_status"]["vendor_green"]["certi"]),
        ("pitch vendor-green", summary["runtime_status"]["vendor_green"]["pitch"]),
    ):
        for vendor in lane_summary.get("vendors", []):
            required_markers = vendor.get("required_markers") or {}
            required_ports = vendor.get("required_ports") or {}
            if required_markers:
                lines.append("")
                lines.append(f"Required markers for `{vendor.get('vendor')}` in `{lane_name}`:")
                for name, marker in required_markers.items():
                    lines.append(f"- `{name}`: `{marker}`")
            if required_ports:
                lines.append("")
                lines.append(f"Required ports for `{vendor.get('vendor')}` in `{lane_name}`:")
                for name, port in required_ports.items():
                    host = port.get("host") or "unknown-host"
                    number = port.get("port")
                    status = port.get("status")
                    rendered_status = f" [{status}]" if status else ""
                    lines.append(f"- `{name}`: `{host}:{number}`{rendered_status}")
    lines.extend(
        [
            "",
            "## Known Gaps",
            "",
        ]
    )
    for profile_name, profile in summary["gap_profiles"].items():
        if profile is None:
            lines.append(f"- `{profile_name}`: no known-gap artifact is currently present")
        else:
            lines.append(
                f"- `{profile_name}`: classification `{profile.get('classification')}`, status `{profile.get('status')}`, "
                f"file `{profile.get('path')}`"
            )
            if profile.get("operator_state"):
                lines.append(f"  - operator-state: `{profile.get('operator_state')}`")
            if profile.get("blocker_summary"):
                lines.append(f"  - blocker: {profile.get('blocker_summary')}")
            next_steps = profile.get("next_steps") or []
            if next_steps:
                for step in next_steps:
                    lines.append(f"  - next: `{step}`")
            artifact_refs = profile.get("operator_artifact_refs") or []
            if artifact_refs:
                for ref in artifact_refs:
                    lines.append(f"  - artifact: `{ref}`")
    lines.extend(
        [
            "",
            "## Probe Stability",
            "",
        ]
    )
    for profile_name, stability in summary["probe_stability"].items():
        if stability is None:
            lines.append(f"- `{profile_name}`: no stability artifact is currently present")
        else:
            lines.append(
                f"- `{profile_name}`: stable `{stability.get('stable')}`, "
                f"success `{stability.get('success_count')}` / attempts `{stability.get('attempt_count')}`, "
                f"promotion `{stability.get('promotion_readiness')}`, "
                f"file `{stability.get('path')}`"
            )
    lines.extend(
        [
            "",
            "## Promotion Review",
            "",
        ]
    )
    review = summary["probe_promotion_review"]
    if review is None:
        lines.append("- no promotion-review artifact is currently present")
    else:
        lines.append(f"- candidate count: `{review.get('candidate_count')}`")
        for row in review.get("profiles") or []:
            lines.append(
                f"- `{row.get('profile')}`: decision `{row.get('review_decision')}`, "
                f"readiness `{row.get('promotion_readiness') or 'missing'}`, docs `{row.get('docs_ref')}`"
            )
            if row.get("next_action"):
                lines.append(f"  - next: {row.get('next_action')}")
    lines.extend(
        [
            "",
            "## Packet Files",
            "",
            f"- JSON summary: `{paths.summary_json.name}`",
            f"- Artifact manifest CSV: `{paths.artifact_manifest_csv.name}`",
            f"- Markdown report: `{paths.report_markdown.name}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n")
    return path


def write_vendor_parity_artifacts(output_dir: Path | str) -> VendorParityArtifactPaths:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    paths = VendorParityArtifactPaths(
        output_dir=output_path,
        summary_json=output_path / "vendor_parity_artifacts_summary.json",
        artifact_manifest_csv=output_path / "vendor_parity_artifacts_manifest.csv",
        report_markdown=output_path / "vendor_parity_artifacts_report.md",
    )
    rows = _build_rows()
    summary = _build_summary(rows)
    paths.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    _write_manifest_csv(paths.artifact_manifest_csv, rows)
    _write_markdown(paths.report_markdown, summary, paths)
    return paths


__all__ = [
    "VendorParityArtifactPaths",
    "VendorParityArtifactRow",
    "write_vendor_parity_artifacts",
]
