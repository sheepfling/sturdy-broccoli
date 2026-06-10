from __future__ import annotations

import argparse
from pathlib import Path

from hla2010.requirements_backlog import write_imported_hla_backlog

REPO_ROOT = Path(__file__).resolve().parents[1]


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
        print(path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
