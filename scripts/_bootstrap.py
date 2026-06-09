"""Shared import-path bootstrap for repo-local scripts and examples."""
from __future__ import annotations

import sys
from pathlib import Path


def _prepend(path: Path) -> None:
    resolved = str(path)
    if path.exists() and resolved not in sys.path:
        sys.path.insert(0, resolved)


REPO_ROOT = Path(__file__).resolve().parents[1]

_prepend(REPO_ROOT)
_prepend(REPO_ROOT / "src")
_prepend(REPO_ROOT / "packages/hla2010-rti-python/src")
_prepend(REPO_ROOT / "packages/hla2010-rti-certi/src")
_prepend(REPO_ROOT / "packages/hla2010-rti-backend-common/src")
_prepend(REPO_ROOT / "packages/hla2010-rti-java-common/src")
_prepend(REPO_ROOT / "packages/hla2010-rti-runtime-common/src")
_prepend(REPO_ROOT / "packages/hla2010-rti-java-jpype/src")
_prepend(REPO_ROOT / "packages/hla2010-rti-java-py4j/src")
_prepend(REPO_ROOT / "packages/hla2010-rti-pitch-common/src")
_prepend(REPO_ROOT / "packages/hla2010-rti-pitch-jpype/src")
_prepend(REPO_ROOT / "packages/hla2010-rti-pitch-py4j/src")
_prepend(REPO_ROOT / "packages/hla2010-rti-portico/src")
_prepend(REPO_ROOT / "packages/hla2010-rti-transport-grpc/src")
_prepend(REPO_ROOT / "packages/hla2010-rti-transport-rest/src")
_prepend(REPO_ROOT / "packages/hla2010-fom-target-radar/src")
_prepend(REPO_ROOT / "packages/hla2010-verification-harness/src")
