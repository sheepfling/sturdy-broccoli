#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
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

from hla.verification.repo_internal.fom_corpus_classification import write_fom_corpus_classification


DEFAULT_OUTPUT_DIR = Path.cwd() / "analysis" / "fom_corpus_classification"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify the current FOM/XML inventory into validation-oriented buckets with edition-scope labels.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for the generated corpus classification report.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional custom report title.",
    )
    args = parser.parse_args(argv)

    json_path, md_path, report = write_fom_corpus_classification(output_root=args.output_dir, title=args.title or "FOM Corpus Classification")
    print(json_path)
    print(md_path)
    print(f"records: {report.total_records}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
