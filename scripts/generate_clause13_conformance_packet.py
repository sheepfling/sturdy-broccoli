from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

import hla2010
from hla2010.clause13_conformance import (
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
