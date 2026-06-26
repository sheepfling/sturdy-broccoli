#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from validate_test_surface_manifest import manifest_path as validator_manifest_path
from validate_test_surface_manifest import validate_manifest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "testing" / "test_surface_manifest.json"
ARTIFACT_DIR = ROOT / "artifacts" / "test_surface_status"
_PRESERVE_DRY_RUN_FRONT_DOORS = {
    "./tools/compliance",
    "./tools/python",
    "./tools/section8-gate",
    "./tools/test",
}
LANE_ALIASES = {
    "repo-units": "repo-green-units",
    "foundation": "unit-foundation",
    "python-core": "unit-python-core",
    "examples": "unit-federate-examples",
    "onboarding": "unit-vendor-onboarding",
    "shim-tooling": "unit-shim-tooling",
    "fom": "unit-fom-tooling",
    "python-2025": "unit-python-2025-core",
    "transport": "unit-transport-local",
    "scenarios": "unit-scenarios-light",
}


@dataclass(frozen=True)
class Lane:
    lane_id: str
    title: str
    description: str
    owner_command: tuple[str, ...]
    commands: tuple[tuple[str, ...], ...]
    include_lanes: tuple[str, ...]
    docs: tuple[str, ...]
    estimated_cost: str
    audience: tuple[str, ...]
    preflight: dict[str, Any]

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "Lane":
        return cls(
            lane_id=str(payload["id"]),
            title=str(payload["title"]),
            description=str(payload["description"]),
            owner_command=tuple(str(item) for item in payload.get("owner_command", [])),
            commands=tuple(tuple(str(part) for part in command) for command in payload.get("commands", [])),
            include_lanes=tuple(str(item) for item in payload.get("include_lanes", [])),
            docs=tuple(str(item) for item in payload.get("docs", [])),
            estimated_cost=str(payload.get("estimated_cost", "")),
            audience=tuple(str(item) for item in payload.get("audience", [])),
            preflight=dict(payload.get("preflight", {})),
        )


def load_manifest() -> list[Lane]:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return [Lane.from_mapping(item) for item in payload["lanes"]]


def lane_by_id() -> dict[str, Lane]:
    return {lane.lane_id: lane for lane in load_manifest()}


def aliases_for_lane(lane_id: str) -> tuple[str, ...]:
    return tuple(alias for alias, canonical in LANE_ALIASES.items() if canonical == lane_id)


def resolve_lane_id(lane_id: str) -> str:
    return LANE_ALIASES.get(lane_id, lane_id)


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _normalize_command_argv(argv: tuple[str, ...]) -> tuple[str, ...]:
    if not argv:
        return argv
    candidate = argv[0]
    if not candidate.startswith("./"):
        return argv
    path = ROOT / candidate[2:]
    if not path.is_file():
        return argv
    if os.access(path, os.X_OK):
        return argv
    return ("bash", *argv)


def _display_command_argv(argv: tuple[str, ...]) -> tuple[str, ...]:
    if argv and argv[0] in _PRESERVE_DRY_RUN_FRONT_DOORS:
        return argv
    return _normalize_command_argv(argv)


def manifest_structure_payload() -> dict[str, Any]:
    path = validator_manifest_path()
    errors = validate_manifest(path)
    return {
        "status": "passed" if not errors else "failed",
        "manifest": str(path),
        "errors": errors,
    }


def manifest_validation_payload() -> dict[str, Any]:
    from detect_workspace_duplicates import build_duplicate_audit, strict_duplicate_candidates

    payload = manifest_structure_payload()
    duplicate_report = build_duplicate_audit()
    strict_rows = [
        {
            "path": row.path,
            "canonical_path": row.canonical_path,
            "status": row.status,
            "copy_index": row.copy_index,
        }
        for row in strict_duplicate_candidates(duplicate_report)
    ]
    duplicate_errors = [
        f"workspace duplicate candidate: {row['path']} -> {row['canonical_path']} ({row['status']})"
        for row in strict_rows
    ]
    return {
        "status": "passed" if payload["status"] == "passed" and not duplicate_errors else "failed",
        "manifest": payload["manifest"],
        "errors": [*payload["errors"], *duplicate_errors],
        "duplicate_audit": {
            "duplicate_count": duplicate_report.duplicate_count,
            "strict_duplicate_count": len(strict_rows),
            "same_content_count": duplicate_report.same_content_count,
            "different_content_count": duplicate_report.different_content_count,
            "orphan_count": duplicate_report.orphan_count,
            "duplicates": strict_rows,
        },
    }


def ensure_manifest_structure_valid() -> None:
    payload = manifest_structure_payload()
    errors = payload["errors"]
    if errors:
        message = "\n".join(
            [
                f"test surface manifest invalid: {payload['manifest']}",
                *[f"- {error}" for error in errors],
            ]
        )
        raise SystemExit(message)


def _classify_payload(payload: Any, *, returncode: int) -> tuple[str, bool, str]:
    if isinstance(payload, dict):
        if isinstance(payload.get("runnable"), bool):
            runnable = bool(payload["runnable"])
            return ("ready" if runnable else "blocked", runnable, "runnable flag reported by preflight")
        if isinstance(payload.get("ready"), bool):
            ready = bool(payload["ready"])
            return ("ready" if ready else "blocked", ready, "ready flag reported by preflight")
        for key in ("classification", "status", "overall_classification"):
            value = payload.get(key)
            if isinstance(value, str):
                normalized = value.strip().lower()
                if any(token in normalized for token in ("ready", "ok", "runnable", "pass")):
                    return ("ready", True, f"{key}={value}")
                if any(token in normalized for token in ("blocked", "missing", "broken", "fail", "error")):
                    return ("blocked", False, f"{key}={value}")
    if returncode == 0:
        return ("ready", True, "preflight exited successfully")
    return ("blocked", False, f"preflight exited with code {returncode}")


def _run_json_command(argv: tuple[str, ...]) -> dict[str, Any]:
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, check=False)
    stdout = result.stdout.strip()
    payload: Any = {}
    if stdout:
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            decoder = json.JSONDecoder()
            try:
                payload, end = decoder.raw_decode(stdout)
                trailing_output = stdout[end:].strip()
                if trailing_output:
                    payload = {
                        "payload": payload,
                        "trailing_output": trailing_output,
                    }
            except json.JSONDecodeError:
                payload = {"stdout": stdout}
    classification, runnable, reason = _classify_payload(payload, returncode=result.returncode)
    return {
        "argv": list(argv),
        "returncode": result.returncode,
        "classification": classification,
        "runnable": runnable,
        "reason": reason,
        "payload": payload,
        "stderr": result.stderr.strip(),
    }


def evaluate_lane_preflight(lane: Lane) -> dict[str, Any]:
    preflight = lane.preflight
    kind = str(preflight.get("kind", "always-ready"))
    if kind == "always-ready":
        reason = str(preflight.get("reason", "No external preflight required."))
        return {
            "id": lane.lane_id,
            "classification": "ready",
            "runnable": True,
            "reason": reason,
            "checks": [],
        }
    if kind == "aggregate":
        checks = tuple(dict(check) for check in preflight.get("checks", ()))
        results = []
        for check in checks:
            argv = tuple(str(item) for item in check["argv"])
            result = _run_json_command(argv)
            result["id"] = str(check["id"])
            results.append(result)
        policy = str(preflight.get("policy", "all-ready"))
        runnable = all(result["runnable"] for result in results) if policy == "all-ready" else any(
            result["runnable"] for result in results
        )
        classification = "ready" if runnable else "blocked"
        reason = "all vendor preflights ready" if runnable else "one or more vendor preflights blocked"
        return {
            "id": lane.lane_id,
            "classification": classification,
            "runnable": runnable,
            "reason": reason,
            "checks": results,
        }
    raise SystemExit(f"unsupported preflight kind: {kind}")


def _summary_paths(lane_id: str) -> tuple[Path, Path]:
    return ARTIFACT_DIR / f"{lane_id}.json", ARTIFACT_DIR / f"{lane_id}.md"


def _write_summary(lane: Lane, payload: dict[str, Any]) -> tuple[Path, Path]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    json_path, md_path = _summary_paths(lane.lane_id)
    json_path.write_text(_json_dump(payload), encoding="utf-8")
    lines = [
        f"# {lane.title}",
        "",
        f"- lane: `{lane.lane_id}`",
        f"- status: `{payload['status']}`",
        f"- owner command: `{' '.join(lane.owner_command)}`",
        f"- dry run: `{'yes' if payload.get('dry_run') else 'no'}`",
        "",
        "## Commands",
        "",
    ]
    for step in payload["steps"]:
        lines.append(f"- `{' '.join(step['argv'])}` -> `{step['status']}`")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def print_usage() -> None:
    sys.stdout.write(
        "\n".join(
            [
                "usage: ./tools/test-surface [inventory|recommend|preflight|run] [options]",
                "",
                "Canonical test-surface discovery and orchestration front door:",
                "  ./tools/test-surface inventory",
                "  ./tools/test-surface validate",
                "  ./tools/test-surface recommend",
                "  ./tools/test-surface preflight",
                "  ./tools/test-surface run smoke",
                "  ./tools/test-surface run fast",
                "  ./tools/test-surface run repo-green-units",
                "  ./tools/test-surface run unit-foundation",
                "  ./tools/test-surface run unit-python-core",
                "  ./tools/test-surface run unit-federate-examples",
                "  ./tools/test-surface run unit-vendor-onboarding",
                "  ./tools/test-surface run unit-shim-tooling",
                "  ./tools/test-surface run onboarding        # alias for unit-vendor-onboarding",
                "  ./tools/test-surface run shim-tooling      # alias for unit-shim-tooling",
                "  ./tools/test-surface run transport         # alias for unit-transport-local",
                "  ./tools/test-surface run unit-fom-tooling",
                "  ./tools/test-surface run unit-python-2025-core",
                "  ./tools/test-surface run unit-transport-local",
                "  ./tools/test-surface run unit-scenarios-light",
                "  ./tools/test-surface run python1516_2025-main",
                "  ./tools/test-surface run python-routes",
                "  ./tools/test-surface run python1516_2025-routes",
                "  ./tools/test-surface run matrix",
                "",
                "Extension rule:",
                "  - reorder unit shards in repo-green-units.include_lanes",
                "  - edit shard contents inside the matching unit-* lane",
                "  - do not edit full_sequence.py just to reshuffle unit slices",
                "",
                "Use --json for machine-readable output.",
            ]
        )
        + "\n"
    )


def _emit(payload: Any, *, as_json: bool) -> None:
    if as_json:
        sys.stdout.write(_json_dump(payload))
        return
    if isinstance(payload, dict) and "lanes" in payload:
        for lane in payload["lanes"]:
            sys.stdout.write(
                f"{lane['id']}: {lane['title']} [{lane['estimated_cost']}] -> {lane['owner_command']}\n"
            )
        return
    if isinstance(payload, dict) and "recommended_lane" in payload:
        sys.stdout.write(f"recommended: {payload['recommended_command']}\n")
        for row in payload["lanes"]:
            sys.stdout.write(f"{row['id']}: {row['classification']} ({row['reason']})\n")
        return
    if isinstance(payload, list):
        for row in payload:
            sys.stdout.write(f"{row['id']}: {row['classification']} ({row['reason']})\n")
        return
    if isinstance(payload, dict) and "status" in payload:
        sys.stdout.write(f"{payload['lane']}: {payload['status']}\n")
        for step in payload["steps"]:
            sys.stdout.write(f"- {' '.join(step['argv'])}: {step['status']}\n")
        return
    sys.stdout.write(_json_dump(payload))


def command_inventory(*, as_json: bool) -> int:
    lanes = load_manifest()
    payload = {
        "lanes": [
            {
                "id": lane.lane_id,
                "title": lane.title,
                "description": lane.description,
                "owner_command": " ".join(lane.owner_command),
                "aliases": list(aliases_for_lane(lane.lane_id)),
                "estimated_cost": lane.estimated_cost,
                "docs": list(lane.docs),
                "audience": list(lane.audience),
            }
            for lane in lanes
        ]
    }
    _emit(payload, as_json=as_json)
    return 0


def command_validate(*, as_json: bool) -> int:
    payload = manifest_validation_payload()
    if as_json:
        _emit(payload, as_json=True)
    else:
        sys.stdout.write(f"{payload['status']}: {payload['manifest']}\n")
        for error in payload["errors"]:
            sys.stdout.write(f"- {error}\n")
    return 0 if payload["status"] == "passed" else 1


def command_preflight(*, as_json: bool, lane_id: str | None) -> int:
    lanes = lane_by_id()
    selected = [lanes[resolve_lane_id(lane_id)]] if lane_id else list(lanes.values())
    payload = [evaluate_lane_preflight(lane) for lane in selected]
    _emit(payload if lane_id is None else payload[0], as_json=as_json)
    return 0


def command_recommend(*, as_json: bool) -> int:
    lanes = load_manifest()
    evaluations = [evaluate_lane_preflight(lane) for lane in lanes]
    recommended_lane = next((lane for lane, result in zip(lanes, evaluations, strict=True) if result["runnable"]), lanes[0])
    payload = {
        "recommended_lane": recommended_lane.lane_id,
        "recommended_command": " ".join(recommended_lane.owner_command),
        "lanes": evaluations,
    }
    _emit(payload, as_json=as_json)
    return 0


def command_run(*, lane_id: str, as_json: bool, dry_run: bool) -> int:
    lanes = lane_by_id()
    lane = lanes[resolve_lane_id(lane_id)]
    steps: list[dict[str, Any]] = []
    status = "passed"

    def run_lane(current_lane: Lane) -> bool:
        nonlocal status
        lane_override = os.environ.get(
            f"HLA2010_TEST_SURFACE_{current_lane.lane_id.upper().replace('-', '_')}_CMD"
        )
        if lane_override:
            commands = (("sh", "-c", lane_override),)
        elif current_lane.include_lanes:
            commands = ()
        else:
            commands = current_lane.commands

        if current_lane.include_lanes:
            for nested_lane_id in current_lane.include_lanes:
                nested_lane = lanes[nested_lane_id]
                if dry_run:
                    steps.append(
                        {
                            "lane": nested_lane.lane_id,
                            "argv": list(nested_lane.owner_command),
                            "returncode": 0,
                            "status": "planned",
                        }
                    )
                    continue
                nested_status = command_run(lane_id=nested_lane.lane_id, as_json=False, dry_run=False)
                step_status = "passed" if nested_status == 0 else "failed"
                steps.append(
                    {
                        "lane": nested_lane.lane_id,
                        "argv": list(nested_lane.owner_command),
                        "returncode": 0 if nested_status == 0 else 1,
                        "status": step_status,
                    }
                )
                if nested_status != 0:
                    status = "failed"
                    return False
            return True

        for argv in commands:
            normalized_argv = _normalize_command_argv(argv)
            if dry_run:
                steps.append({"argv": list(_display_command_argv(argv)), "returncode": 0, "status": "planned"})
                continue
            result = subprocess.run(normalized_argv, cwd=ROOT, text=True, check=False)
            step_status = "passed" if result.returncode == 0 else "failed"
            steps.append({"argv": list(normalized_argv), "returncode": result.returncode, "status": step_status})
            if result.returncode != 0:
                status = "failed"
                return False
        return True

    run_lane(lane)
    payload = {
        "lane": lane.lane_id,
        "title": lane.title,
        "status": status,
        "dry_run": dry_run,
        "steps": steps,
    }
    json_path, md_path = _write_summary(lane, payload)
    payload["artifacts"] = {"json": str(json_path.relative_to(ROOT)), "markdown": str(md_path.relative_to(ROOT))}
    _emit(payload, as_json=as_json)
    return 0 if status == "passed" else 1


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"help", "-h", "--help"}:
        print_usage()
        return 0
    ensure_manifest_structure_valid()

    args = list(argv[1:])
    as_json = False
    dry_run = False
    lane_id: str | None = None
    if "--json" in args:
        args.remove("--json")
        as_json = True
    if "--dry-run" in args:
        args.remove("--dry-run")
        dry_run = True
    if "--lane" in args:
        index = args.index("--lane")
        try:
            lane_id = args[index + 1]
        except IndexError as exc:
            raise SystemExit("--lane requires an argument") from exc
        del args[index : index + 2]

    command = args[0]
    if command == "validate":
        return command_validate(as_json=as_json)
    if command == "inventory":
        return command_inventory(as_json=as_json)
    if command == "preflight":
        return command_preflight(as_json=as_json, lane_id=lane_id)
    if command == "recommend":
        return command_recommend(as_json=as_json)
    if command == "run":
        if len(args) < 2:
            raise SystemExit("run requires a lane id")
        return command_run(lane_id=args[1], as_json=as_json, dry_run=dry_run)

    raise SystemExit(f"unknown command: {command}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
