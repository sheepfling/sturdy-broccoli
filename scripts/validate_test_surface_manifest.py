#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_PATH = ROOT / "testing" / "test_surface_manifest.json"
DEFAULT_ARTIFACT_DIR = ROOT / "artifacts" / "test_surface_status"


@dataclass(frozen=True)
class Lane:
    lane_id: str
    owner_command: tuple[str, ...]
    commands: tuple[tuple[str, ...], ...]
    include_lanes: tuple[str, ...]

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "Lane":
        return cls(
            lane_id=str(payload.get("id", "")).strip(),
            owner_command=tuple(str(item) for item in payload.get("owner_command", [])),
            commands=tuple(tuple(str(part) for part in command) for command in payload.get("commands", [])),
            include_lanes=tuple(str(item) for item in payload.get("include_lanes", [])),
        )


def manifest_path() -> Path:
    override = os.environ.get("HLA2010_TEST_SURFACE_MANIFEST")
    if override:
        return Path(override)
    return DEFAULT_MANIFEST_PATH


def artifact_dir() -> Path:
    override = os.environ.get("HLA2010_TEST_SURFACE_ARTIFACT_DIR")
    if override:
        return Path(override)
    return DEFAULT_ARTIFACT_DIR


def load_manifest(path: Path) -> list[Lane]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    lanes_payload = payload.get("lanes")
    if not isinstance(lanes_payload, list):
        raise ValueError("manifest must contain a top-level 'lanes' list")
    return [Lane.from_mapping(item) for item in lanes_payload]


def validate_manifest(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        lanes = load_manifest(path)
    except FileNotFoundError:
        return [f"manifest file not found: {path}"]
    except json.JSONDecodeError as exc:
        return [f"manifest is not valid JSON: {exc}"]
    except ValueError as exc:
        return [str(exc)]

    lane_ids = [lane.lane_id for lane in lanes]
    if any(not lane_id for lane_id in lane_ids):
        errors.append("every lane must have a non-empty id")

    seen: set[str] = set()
    duplicates: list[str] = []
    for lane_id in lane_ids:
        if lane_id in seen:
            duplicates.append(lane_id)
        seen.add(lane_id)
    for lane_id in sorted(set(duplicates)):
        errors.append(f"duplicate lane id: {lane_id}")

    lane_map = {lane.lane_id: lane for lane in lanes if lane.lane_id}
    for lane in lanes:
        if not lane.owner_command:
            errors.append(f"lane '{lane.lane_id}' must declare owner_command")
        if lane.commands and lane.include_lanes:
            errors.append(f"lane '{lane.lane_id}' cannot declare both commands and include_lanes")
        if not lane.commands and not lane.include_lanes:
            errors.append(f"lane '{lane.lane_id}' must declare commands or include_lanes")
        duplicate_includes = sorted({nested for nested in lane.include_lanes if lane.include_lanes.count(nested) > 1})
        for nested in duplicate_includes:
            errors.append(f"lane '{lane.lane_id}' includes '{nested}' more than once")
        for nested in lane.include_lanes:
            if nested not in lane_map:
                errors.append(f"lane '{lane.lane_id}' includes unknown lane '{nested}'")

    visited: set[str] = set()
    active: set[str] = set()

    def walk(lane_id: str, stack: tuple[str, ...]) -> None:
        if lane_id in active:
            cycle = " -> ".join((*stack, lane_id))
            errors.append(f"include_lanes cycle detected: {cycle}")
            return
        if lane_id in visited:
            return
        lane = lane_map.get(lane_id)
        if lane is None:
            return
        active.add(lane_id)
        for nested in lane.include_lanes:
            walk(nested, (*stack, lane_id))
        active.remove(lane_id)
        visited.add(lane_id)

    for lane_id in lane_map:
        walk(lane_id, ())
    return errors


def validation_payload(path: Path) -> dict[str, Any]:
    errors = validate_manifest(path)
    return {
        "status": "passed" if not errors else "failed",
        "manifest": str(path),
        "errors": errors,
    }


def write_validation_artifacts(payload: dict[str, Any], *, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "validate_manifest.json"
    md_path = output_dir / "validate_manifest.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Test Surface Manifest Validation",
        "",
        f"- status: `{payload['status']}`",
        f"- manifest: `{payload['manifest']}`",
        "",
    ]
    if payload["errors"]:
        lines.append("## Errors")
        lines.append("")
        for error in payload["errors"]:
            lines.append(f"- {error}")
    else:
        lines.append("No manifest errors detected.")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    path = manifest_path()
    payload = validation_payload(path)
    write_validation_artifacts(payload, output_dir=artifact_dir())
    errors = payload["errors"]
    if errors:
        sys.stderr.write(f"test surface manifest invalid: {path}\n")
        for error in errors:
            sys.stderr.write(f"- {error}\n")
        return 1
    sys.stdout.write(f"test surface manifest valid: {path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
