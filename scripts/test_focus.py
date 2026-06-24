#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "testing" / "test_focus_manifest.json"
ARTIFACT_DIR = ROOT / "analysis" / "test_focus_status"


@dataclass(frozen=True)
class Target:
    target_id: str
    title: str
    description: str
    owner_packages: tuple[str, ...]
    estimated_cost: str
    commands: tuple[tuple[str, ...], ...]

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "Target":
        return cls(
            target_id=str(payload["id"]),
            title=str(payload["title"]),
            description=str(payload["description"]),
            owner_packages=tuple(str(item) for item in payload.get("owner_packages", [])),
            estimated_cost=str(payload.get("estimated_cost", "")),
            commands=tuple(tuple(str(part) for part in command) for command in payload.get("commands", [])),
        )


def load_manifest() -> list[Target]:
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return [Target.from_mapping(item) for item in payload["targets"]]


def target_by_id() -> dict[str, Target]:
    return {target.target_id: target for target in load_manifest()}


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _emit(payload: Any, *, as_json: bool) -> None:
    if as_json:
        sys.stdout.write(_json_dump(payload))
        return
    if isinstance(payload, dict) and "targets" in payload:
        for target in payload["targets"]:
            sys.stdout.write(
                f"{target['id']}: {target['title']} [{target['estimated_cost']}] "
                f"owners={','.join(target['owner_packages'])}\n"
            )
        return
    if isinstance(payload, dict) and "target" in payload and "status" in payload:
        sys.stdout.write(f"{payload['target']}: {payload['status']}\n")
        for step in payload["steps"]:
            sys.stdout.write(f"- {' '.join(step['argv'])}: {step['status']}\n")
        return
    sys.stdout.write(_json_dump(payload))


def _summary_paths(target_id: str) -> tuple[Path, Path]:
    return ARTIFACT_DIR / f"{target_id}.json", ARTIFACT_DIR / f"{target_id}.md"


def _write_summary(payload: dict[str, Any]) -> tuple[Path, Path]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    json_path, md_path = _summary_paths(payload["target"])
    json_path.write_text(_json_dump(payload), encoding="utf-8")
    lines = [
        f"# {payload['title']}",
        "",
        f"- target: `{payload['target']}`",
        f"- status: `{payload['status']}`",
        f"- estimated cost: `{payload['estimated_cost']}`",
        f"- owner packages: `{', '.join(payload['owner_packages'])}`",
        f"- last failed mode: `{'yes' if payload['last_failed'] else 'no'}`",
        f"- failed first mode: `{'yes' if payload['failed_first'] else 'no'}`",
        f"- dry run: `{'yes' if payload['dry_run'] else 'no'}`",
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
                "usage: ./tools/test-focus [inventory|run|resume] [options] [-- pytest-args...]",
                "",
                "Named focused-test front door for speed and restartability:",
                "  ./tools/test-focus inventory",
                "  ./tools/test-focus run foundation",
                "  ./tools/test-focus run python-examples",
                "  ./tools/test-focus run java-bridges",
                "  ./tools/test-focus run jpype",
                "  ./tools/test-focus run target-radar",
                "  ./tools/test-focus run python-2025-runtime -- --maxfail=1",
                "  ./tools/test-focus resume python-2025-runtime",
                "",
                "Options:",
                "  --json         machine-readable output",
                "  --dry-run      plan commands without running them",
                "  --lf           rerun only last failures for the selected target",
                "  --ff           run previous failures first for the selected target",
            ]
        )
        + "\n"
    )


def command_inventory(*, as_json: bool) -> int:
    payload = {
        "targets": [
            {
                "id": target.target_id,
                "title": target.title,
                "description": target.description,
                "owner_packages": list(target.owner_packages),
                "estimated_cost": target.estimated_cost,
                "commands": [list(command) for command in target.commands],
            }
            for target in load_manifest()
        ]
    }
    _emit(payload, as_json=as_json)
    return 0


def _extend_command(command: tuple[str, ...], *, last_failed: bool, failed_first: bool, extra_args: list[str]) -> list[str]:
    argv = list(command)
    if len(argv) >= 2 and argv[0] == "./tools/test":
        if last_failed:
            argv.append("--lf")
        if failed_first:
            argv.append("--ff")
        argv.extend(extra_args)
        return argv
    return argv + extra_args


def command_run(*, target_id: str, as_json: bool, dry_run: bool, last_failed: bool, failed_first: bool, extra_args: list[str]) -> int:
    targets = target_by_id()
    target = targets[target_id]
    steps: list[dict[str, Any]] = []
    status = "passed"
    for command in target.commands:
        argv = _extend_command(command, last_failed=last_failed, failed_first=failed_first, extra_args=extra_args)
        if dry_run:
            steps.append({"argv": argv, "returncode": 0, "status": "planned"})
            continue
        result = subprocess.run(argv, cwd=ROOT, text=True, check=False)
        step_status = "passed" if result.returncode == 0 else "failed"
        steps.append({"argv": argv, "returncode": result.returncode, "status": step_status})
        if result.returncode != 0:
            status = "failed"
            break
    payload = {
        "target": target.target_id,
        "title": target.title,
        "description": target.description,
        "owner_packages": list(target.owner_packages),
        "estimated_cost": target.estimated_cost,
        "status": status,
        "last_failed": last_failed,
        "failed_first": failed_first,
        "dry_run": dry_run,
        "steps": steps,
    }
    json_path, md_path = _write_summary(payload)
    payload["artifacts"] = {"json": str(json_path.relative_to(ROOT)), "markdown": str(md_path.relative_to(ROOT))}
    _emit(payload, as_json=as_json)
    return 0 if status == "passed" else 1


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"help", "-h", "--help"}:
        print_usage()
        return 0

    args = list(argv[1:])
    extra_args: list[str] = []
    if "--" in args:
        index = args.index("--")
        extra_args = args[index + 1 :]
        args = args[:index]

    as_json = False
    dry_run = False
    last_failed = False
    failed_first = False
    if "--json" in args:
        args.remove("--json")
        as_json = True
    if "--dry-run" in args:
        args.remove("--dry-run")
        dry_run = True
    if "--lf" in args:
        args.remove("--lf")
        last_failed = True
    if "--ff" in args:
        args.remove("--ff")
        failed_first = True

    command = args[0]
    if command == "inventory":
        return command_inventory(as_json=as_json)
    if command == "run":
        if len(args) < 2:
            raise SystemExit("run requires a target id")
        return command_run(
            target_id=args[1],
            as_json=as_json,
            dry_run=dry_run,
            last_failed=last_failed,
            failed_first=failed_first,
            extra_args=extra_args,
        )
    if command == "resume":
        if len(args) < 2:
            raise SystemExit("resume requires a target id")
        return command_run(
            target_id=args[1],
            as_json=as_json,
            dry_run=dry_run,
            last_failed=True,
            failed_first=failed_first,
            extra_args=extra_args,
        )

    raise SystemExit(f"unknown command: {command}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
