#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import ssl
import sys
import tomllib
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm, HTTPSHandler, build_opener

try:
    import certifi
except ModuleNotFoundError:  # pragma: no cover - optional environment support
    certifi = None

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()


@dataclass(frozen=True, slots=True)
class DownloadLink:
    url: str
    text: str


class _LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[DownloadLink] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attr_map = dict(attrs)
        href = attr_map.get("href")
        if not href:
            return
        self._href = href
        self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._href is None:
            return
        self.links.append(DownloadLink(url=self._href, text="".join(self._text).strip()))
        self._href = None
        self._text = []


def _maybe_source_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def _env_file_from_argv(argv: list[str] | None) -> Path:
    values = list(argv or [])
    for index, token in enumerate(values):
        if token == "--env-file" and index + 1 < len(values):
            return Path(values[index + 1])
        if token.startswith("--env-file="):
            return Path(token.split("=", 1)[1])
    return Path(SCRIPT_REPO_ROOT / ".local" / "siso-download.env")


def _ssl_context() -> ssl.SSLContext | None:
    if certifi is None:
        return None
    return ssl.create_default_context(cafile=certifi.where())


def _download_opener(base_url: str) -> object:
    username = os.environ.get("SISO_USERNAME")
    password = os.environ.get("SISO_PASSWORD")
    https_handler = HTTPSHandler(context=_ssl_context())
    if not username or not password:
        return build_opener(https_handler)
    parsed = urlparse(base_url)
    mgr = HTTPPasswordMgrWithDefaultRealm()
    mgr.add_password(None, f"{parsed.scheme}://{parsed.netloc}", username, password)
    return build_opener(HTTPBasicAuthHandler(mgr), https_handler)


def _extract_download_links(base_url: str, html_text: str) -> list[DownloadLink]:
    parser = _LinkCollector()
    parser.feed(html_text)
    links: list[DownloadLink] = []
    for item in parser.links:
        full_url = urljoin(base_url, item.url)
        parsed = urlparse(full_url)
        if parsed.netloc and parsed.netloc != urlparse(base_url).netloc:
            continue
        if re.search(r"\.(zip|xml|xsd)$", parsed.path, re.IGNORECASE):
            links.append(DownloadLink(url=full_url, text=item.text))
            continue
        if any(token in full_url.lower() or token in item.text.lower() for token in ("fom", "rpr", "1516", "omt", "mim")):
            links.append(DownloadLink(url=full_url, text=item.text))
    deduped: list[DownloadLink] = []
    seen: set[str] = set()
    for item in links:
        if item.url in seen:
            continue
        seen.add(item.url)
        deduped.append(item)
    return deduped


def _download_file(opener: object, url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with opener.open(url) as response:  # type: ignore[attr-defined]
        destination.write_bytes(response.read())


def main(argv: list[str] | None = None) -> int:
    _maybe_source_env_file(_env_file_from_argv(argv))
    parser = argparse.ArgumentParser(description="Download authenticated SISO DataFiles-linked FOM packages.")
    parser.add_argument(
        "--url",
        default=os.environ.get("SISO_DATAFILES_URL", "https://www.sisostandards.org/page/DataFiles"),
        help="SISO DataFiles page URL.",
    )
    parser.add_argument(
        "--out",
        default=os.environ.get("SISO_DOWNLOAD_DIR", str(SCRIPT_REPO_ROOT / "artifacts" / "siso_downloads")),
        help="Destination directory for downloaded files.",
    )
    parser.add_argument(
        "--env-file",
        default=str(SCRIPT_REPO_ROOT / ".local" / "siso-download.env"),
        help="Optional env file to source before resolving credentials.",
    )
    args = parser.parse_args(argv)

    opener = _download_opener(args.url)
    with opener.open(args.url) as response:  # type: ignore[attr-defined]
        html_text = response.read().decode("utf-8", errors="replace")

    links = _extract_download_links(args.url, html_text)
    output_root = Path(args.out)
    output_root.mkdir(parents=True, exist_ok=True)
    for link in links:
        filename = Path(urlparse(link.url).path).name
        if not filename:
            continue
        destination = output_root / filename
        _download_file(opener, link.url, destination)
        print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
