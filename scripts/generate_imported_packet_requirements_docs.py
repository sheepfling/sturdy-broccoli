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

from hla2010_repo_internal.requirements_packet import write_imported_hla_packet_markdown_views

REPO_ROOT = Path.cwd()


def _display_path(path: Path, repo_root: Path) -> Path:
    try:
        return path.relative_to(repo_root)
    except ValueError:
        return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate markdown views from the imported HLA requirements packet."
    )
    parser.add_argument(
        "--output-dir",
        default="docs/verification/imported_packet_requirements_v1_0",
        help="Directory to receive the generated markdown views.",
    )
    args = parser.parse_args(argv)

    repo_root = REPO_ROOT
    written = write_imported_hla_packet_markdown_views(repo_root / args.output_dir, repo_root)
    for path in sorted(written.values()):
        print(_display_path(path, repo_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
