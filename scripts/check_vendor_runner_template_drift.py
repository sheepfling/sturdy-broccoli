#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import site


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_workspace_imports() -> None:
    for source_root in (PROJECT_ROOT / "src", *sorted((PROJECT_ROOT / "packages").glob("*/src"))):
        if source_root.is_dir():
            site.addsitedir(str(source_root))


_bootstrap_workspace_imports()

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
