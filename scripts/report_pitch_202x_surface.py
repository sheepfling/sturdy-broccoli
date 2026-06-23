#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    for root in reversed(pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]):
        source_path = str(REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


def main() -> int:
    _bootstrap()
    from hla.verification.repo_internal.pitch_202x_surface_audit import (
        build_pitch_202x_surface_audit,
        write_pitch_202x_surface_audit,
    )

    output_dir = REPO_ROOT / "packages/hla-vendor-pitch/docs/evidence"
    output_dir.mkdir(parents=True, exist_ok=True)
    report = build_pitch_202x_surface_audit(REPO_ROOT)
    json_path = output_dir / "pitch_202x_surface_audit_2026-06-23.json"
    markdown_path = output_dir / "pitch_202x_surface_audit_2026-06-23.md"
    write_pitch_202x_surface_audit(report, json_path, markdown_path)
    print(json_path)
    print(markdown_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
