#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path.cwd()


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla2010_repo_internal.verification.vendor_runner_template_drift import write_vendor_runner_template_drift


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check for drift between the runner provisioning template, validator profiles, and workflow env contracts.")
    parser.add_argument(
        "--template",
        default=str(PROJECT_ROOT / "docs" / "vendor_runner_provisioning_template.yaml"),
        help="Path to the runner provisioning template YAML.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "analysis" / "vendor_runner_template_drift"),
        help="Directory for generated drift reports.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON summary to stdout.")
    args = parser.parse_args(argv)

    paths = write_vendor_runner_template_drift(args.output_dir, template_path=args.template)
    if args.json:
        print(paths.summary_json.read_text(encoding="utf-8"), end="")
    else:
        print(paths.summary_json)
        print(paths.report_markdown)
    payload = json.loads(paths.summary_json.read_text(encoding="utf-8"))
    return int(payload["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
