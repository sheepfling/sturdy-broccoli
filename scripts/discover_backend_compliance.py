#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

DEFAULT_PROJECT_ROOT = Path.cwd()
SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_SCRIPT = Path(__file__).resolve().with_name("generate_compliance_artifacts.py")


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()


def _bootstrapped_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(sys.path)
    return env

from hla2010_repo_internal.verification.backend_compliance_discovery import (
    build_discovery_payload,
    render_backend_compliance_catalog_text,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover backend compliance and parity from the generated compliance artifacts."
    )
    parser.add_argument("--refresh", action="store_true", help="Regenerate analysis/compliance artifacts before reading them.")
    parser.add_argument("--backend", help="Filter the text output to one backend id or backend family.")
    parser.add_argument("--show-backlog", action="store_true", help="Show ranked vendor discovery backlog rows after the backend summary.")
    parser.add_argument("--priority", help="Filter backlog rows by priority label or current status.")
    parser.add_argument("--section", help="Filter backlog rows by section root, section ref, or requirement id.")
    parser.add_argument("--project-root", type=Path, default=DEFAULT_PROJECT_ROOT, help="Repository root for generated compliance artifacts.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    args = parser.parse_args()
    project_root = args.project_root.resolve()

    if args.refresh:
        subprocess.run(
            [
                sys.executable,
                str(GENERATOR_SCRIPT),
                "--project-root",
                str(project_root),
            ],
            cwd=project_root,
            env=_bootstrapped_env(),
            check=True,
        )

    payload = build_discovery_payload(
        project_root,
        backend_filter=args.backend,
        section_filter=args.section,
        priority_filter=args.priority,
    )
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        sys.stdout.write(
            render_backend_compliance_catalog_text(
                payload["catalog"],
                backend_filter=args.backend,
                backlog=payload["backlog"] if args.show_backlog else None,
                section_filter=args.section,
                priority_filter=args.priority,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
