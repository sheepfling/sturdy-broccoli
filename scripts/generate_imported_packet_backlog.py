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

from hla2010_repo_internal.requirements_backlog import write_imported_hla_backlog

REPO_ROOT = Path.cwd()


def _display_path(path: Path) -> Path:
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate implementation backlog views from the imported HLA packet and harmonized ledgers."
    )
    parser.add_argument(
        "--markdown",
        default="docs/plans/imported_requirements_backlog_v1_0.md",
        help="Path to the generated markdown backlog.",
    )
    parser.add_argument(
        "--json",
        default="docs/plans/imported_requirements_backlog_v1_0.json",
        help="Path to the generated JSON backlog.",
    )
    args = parser.parse_args(argv)

    written = write_imported_hla_backlog(
        REPO_ROOT / args.markdown,
        REPO_ROOT / args.json,
        REPO_ROOT,
    )
    for path in written.values():
        print(_display_path(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
