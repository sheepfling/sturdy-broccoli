#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import ssl
import urllib.request
from pathlib import Path
from typing import Any

try:
    import certifi
except ModuleNotFoundError:  # pragma: no cover - optional environment support
    certifi = None


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "third_party" / "fom_baseline" / "manifest" / "public_fom_baseline_sources.json"


def _raw_url(repository: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{repository}/master/{path}"


def _write_source_index(manifest: dict[str, Any], output_root: Path) -> None:
    lines = ["# Public FOM Baseline Source Index", ""]
    for family in manifest["families"]:
        lines.append(f"## {family['name']}")
        lines.append(f"- id: `{family['id']}`")
        lines.append(f"- repository: `{family['repository']}`")
        lines.append(f"- load mode: `{family['load_mode']}`")
        lines.append(f"- round-trip mode: `{family['roundtrip_mode']}`")
        lines.append(f"- license note: {family['license_note']}")
        lines.append("")
        for file_path in family["files"]:
            lines.append(f"- `{file_path}`")
            lines.append(f"  raw: `{_raw_url(family['repository'], file_path)}`")
        lines.append("")
    (output_root / "SOURCE_INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def _fetch_file(repository: str, path: str, output_root: Path) -> Path:
    destination = output_root / repository / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    context = ssl.create_default_context(cafile=certifi.where()) if certifi is not None else None
    with urllib.request.urlopen(_raw_url(repository, path), timeout=60, context=context) as response:
        destination.write_bytes(response.read())
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh the public FOM XML baseline from the curated manifest.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--out-root", default=str(REPO_ROOT / "third_party" / "fom_baseline" / "upstream"))
    args = parser.parse_args(argv)

    manifest_path = Path(args.manifest)
    output_root = Path(args.out_root)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output_root.mkdir(parents=True, exist_ok=True)

    for family in manifest["families"]:
        repository = str(family["repository"])
        for file_path in family["files"]:
            destination = _fetch_file(repository, str(file_path), output_root)
            print(destination)

    _write_source_index(manifest, output_root.parent)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
