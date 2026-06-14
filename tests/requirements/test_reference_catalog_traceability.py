from __future__ import annotations

import csv
from pathlib import Path

from hla2010_repo_internal.traceability import _file_anchor_exists, path_exists, split_refs
from tests.compliance_row_models import ReferenceCsvRow


ROOT = Path(__file__).resolve().parents[2]
REFERENCE_DIR = ROOT / "requirements" / "reference"
REF_PREFIXES = (
    "tests/",
    "requirements/",
    "docs/",
    "analysis/",
    "examples/",
    "src/",
    "packages/",
    "hla2010/",
)


def _candidate_refs(row: ReferenceCsvRow) -> list[str]:
    refs: list[str] = []
    for value in row.values():
        for ref in split_refs(value):
            if ref.startswith(("generated:", "external:")):
                continue
            if ref.startswith(REF_PREFIXES):
                refs.append(ref)
    return refs


def test_reference_requirement_catalog_refs_resolve() -> None:
    unresolved: list[str] = []
    for path in sorted(REFERENCE_DIR.glob("*.csv")):
        with path.open(newline="", encoding="utf-8") as handle:
            rows = [ReferenceCsvRow.from_mapping(row) for row in csv.DictReader(handle)]
        for index, row in enumerate(rows, start=2):
            for ref in _candidate_refs(row):
                if path_exists(ref) or _file_anchor_exists(ref):
                    continue
                unresolved.append(f"{path.relative_to(ROOT).as_posix()}:{index}: {ref}")
    assert not unresolved, "\n".join(unresolved)
