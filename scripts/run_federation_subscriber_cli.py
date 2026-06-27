from __future__ import annotations

import argparse
import json
import sys
import time
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla.verification.repo_internal.verification.runtime_observer_core import RuntimeObserverControl, build_runtime_observer_catalog


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Observer CLI over the shared federation subscriber core.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    catalog = subparsers.add_parser("catalog", help="Print the available observer providers and scenarios.")
    catalog.add_argument("--json", action="store_true", help="Emit raw JSON.")

    observe = subparsers.add_parser("observe", help="Start one observer session and stream state snapshots.")
    observe.add_argument("--provider", default="siso-runtime", choices=("siso-runtime", "two-federate", "target-radar", "live-federation"))
    observe.add_argument("--scenario", required=True)
    observe.add_argument("--output-dir", type=Path, default=Path.cwd() / "artifacts" / "federation_visualizer_cli")
    observe.add_argument("--backend", default=None)
    observe.add_argument("--target-radar-steps", type=int, default=None)
    observe.add_argument("--poll-seconds", type=float, default=0.5)
    observe.add_argument("--json", action="store_true", help="Emit the final state as JSON.")
    return parser


def _print_catalog(json_output: bool) -> int:
    catalog = build_runtime_observer_catalog()
    if json_output:
        print(json.dumps(catalog, indent=2, sort_keys=True))
        return 0
    for provider in catalog["providers"]:
        print(f"{provider['provider']}: {provider['label']}")
        for row in provider["scenarios"]:
            print(f"  - {row['id']}: {row['label']}")
    return 0


def _render_state_snapshot(state: dict[str, object]) -> str:
    metrics = state.get("live_metrics") if isinstance(state.get("live_metrics"), dict) else {}
    objects = ((state.get("inspectors") or {}).get("objects") if isinstance(state.get("inspectors"), dict) else []) or []
    interactions = ((state.get("inspectors") or {}).get("interactions") if isinstance(state.get("inspectors"), dict) else []) or []
    lines = [
        f"status: {state.get('status', 'unknown')}",
        f"provider: {state.get('provider', '')}",
        f"scenario: {state.get('scenario', '')}",
        f"backend: {state.get('backend', '')}",
        f"events: {metrics.get('event_count', 0) if isinstance(metrics, dict) else 0}",
        f"objects: {len(objects)}",
        f"interactions: {len(interactions)}",
        f"story: {state.get('story', '')}",
    ]
    recent_events = state.get("normalized_events") or []
    if isinstance(recent_events, list) and recent_events:
        lines.append("recent:")
        for row in recent_events[-5:]:
            if not isinstance(row, dict):
                continue
            lines.append(
                f"  - #{row.get('sequence', '?')} {row.get('event_type', '')} "
                f"{row.get('class_name') or row.get('interaction_class') or row.get('phase') or row.get('operation') or ''}"
            )
    return "\n".join(lines)


def _observe(args: argparse.Namespace) -> int:
    options: dict[str, object] = {}
    if args.target_radar_steps is not None:
        options["target_radar_steps"] = int(args.target_radar_steps)
    control = RuntimeObserverControl(output_dir=args.output_dir, default_backend=args.backend)
    session = control.start(
        provider=str(args.provider),
        scenario=str(args.scenario),
        backend=None if args.backend is None else str(args.backend),
        options=options,
    )
    try:
        while True:
            state = session.live_state()
            if args.json:
                print(json.dumps(state, indent=2, sort_keys=True))
            else:
                print(_render_state_snapshot(state))
                print("")
            if state.get("status") in {"complete", "failed", "stopped"}:
                break
            time.sleep(float(args.poll_seconds))
    finally:
        if session.live_state().get("status") == "running":
            session.stop()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "catalog":
        return _print_catalog(bool(args.json))
    if args.command == "observe":
        return _observe(args)
    raise SystemExit(f"unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
