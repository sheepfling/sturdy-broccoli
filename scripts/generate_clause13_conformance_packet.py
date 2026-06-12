from __future__ import annotations

import sys
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path.cwd()


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

import hla2010
from hla2010_repo_internal.verification.clause13_conformance import (
    write_clause13_conformance_packet_json,
    write_clause13_conformance_packet_markdown,
)

OUTPUT_DIR = REPO_ROOT / "docs" / "verification"


def main() -> int:
    write_clause13_conformance_packet_json(
        OUTPUT_DIR / "clause13_conformance_packet.json",
        REPO_ROOT,
        version=hla2010.__version__,
    )
    write_clause13_conformance_packet_markdown(
        OUTPUT_DIR / "clause13_conformance_packet.md",
        REPO_ROOT,
        version=hla2010.__version__,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
