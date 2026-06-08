from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hla2010.requirements_packet import write_imported_hla_packet_markdown_views


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
        print(path.relative_to(repo_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
