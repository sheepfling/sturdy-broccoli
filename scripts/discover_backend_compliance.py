#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
import site


REPO_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_workspace_imports() -> None:
    for source_root in (REPO_ROOT / "src", *sorted((REPO_ROOT / "packages").glob("*/src"))):
        if source_root.is_dir():
            site.addsitedir(str(source_root))


_bootstrap_workspace_imports()

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
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    args = parser.parse_args()

    if args.refresh:
        subprocess.run([sys.executable, "scripts/generate_compliance_artifacts.py"], cwd=REPO_ROOT, check=True)

    payload = build_discovery_payload(
        REPO_ROOT,
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
