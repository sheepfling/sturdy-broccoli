#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import _bootstrap  # noqa: F401

REPO_ROOT = Path(__file__).resolve().parents[1]

from hla2010.fom_overview import main

if __name__ == "__main__":
    raise SystemExit(main())
