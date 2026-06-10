#!/usr/bin/env python3
"""Download official IEEE HLA ZIP resources provided by the user.

The generator environment used for this prototype could verify the URLs but was
not allowed to save application/zip content. Run this script locally.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from urllib.request import Request, urlopen

URLS = {
    "1516-2025_downloads.zip": "https://standards.ieee.org/wp-content/uploads/2025/05/1516-2025_downloads.zip",
    "1516.1-2010_downloads.zip": "https://standards.ieee.org/wp-content/uploads/import/download/1516.1-2010_downloads.zip",
    "1516.2-2010_downloads.zip": "https://standards.ieee.org/wp-content/uploads/import/download/1516.2-2010_downloads.zip",
}


def download(url: str, destination: Path) -> None:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=90) as response:
        data = response.read()
    destination.write_bytes(data)
    print(f"wrote {destination} ({len(data):,} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(os.environ.get("HLA2010_DOWNLOADS_DIR", "analysis/downloads")),
    )
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for filename, url in URLS.items():
        download(url, args.out / filename)


if __name__ == "__main__":
    main()
