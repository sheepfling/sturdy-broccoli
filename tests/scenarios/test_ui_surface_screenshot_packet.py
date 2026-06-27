from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from scripts.generate_ui_surface_screenshot_packet import (
    _capture_live_federate_service,
    _capture_live_visualizer,
    _write_index_html,
    _write_manifest,
)


def test_ui_surface_screenshot_packet_help() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        ["python3", "scripts/generate_ui_surface_screenshot_packet.py", "--help"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Generate a deterministic browser screenshot packet" in result.stdout
    assert "--output-dir" in result.stdout
    assert "--live-visualizer-url" in result.stdout
    assert "--live-federate-service-url" in result.stdout
    assert "--live-only" in result.stdout


def test_ui_surface_screenshot_packet_live_only_requires_live_url() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        ["python3", "scripts/generate_ui_surface_screenshot_packet.py", "--live-only"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "--live-only requires --live-visualizer-url and/or --live-federate-service-url." in result.stderr


def test_ui_surface_screenshot_packet_gallery_files(tmp_path: Path) -> None:
    captures = [
        {
            "title": "Workbench Overview",
            "description": "Seeded capture for the workbench surface.",
            "image_rel": "workbench-overview.png",
            "source": "fom_workbench/index.html",
        },
        {
            "title": "Live Visualizer Overview",
            "description": "Live capture for the visualizer surface.",
            "image_rel": "live-visualizer-overview.png",
            "source": "http://127.0.0.1:9000/",
        },
    ]
    index_path = _write_index_html(tmp_path, browser_name="chromium", captures=captures)
    manifest_path = _write_manifest(
        tmp_path,
        browser_name="chromium",
        captures=captures,
        index_path=index_path,
    )

    index_html = index_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert index_path.exists()
    assert manifest_path.exists()
    assert manifest["browser"] == "chromium"
    assert manifest["captures"] == captures
    assert manifest["index_html"] == str(index_path)
    assert "UI Surface Screenshot Packet" in index_html
    for capture in captures:
        assert capture["title"] in index_html
        assert capture["image_rel"] in index_html
        assert capture["source"] in index_html


class _FakeLocator:
    def __init__(self, page: "_FakePage", selector: str) -> None:
        self._page = page
        self._selector = selector

    @property
    def first(self) -> "_FakeLocator":
        return self

    def click(self) -> None:
        self._page.clicks.append(self._selector)

    def screenshot(self, *, path: str) -> None:
        Path(path).write_text(self._selector, encoding="utf-8")
        self._page.screenshots.append((self._selector, path))

    def count(self) -> int:
        return self._page.counts.get(self._selector, 0)


class _FakePage:
    def __init__(self, *, counts: dict[str, int] | None = None) -> None:
        self.counts = counts or {}
        self.gotos: list[str] = []
        self.viewports: list[dict[str, int]] = []
        self.waits: list[tuple[str, Any]] = []
        self.clicks: list[str] = []
        self.screenshots: list[tuple[str, str]] = []

    def set_viewport_size(self, viewport: dict[str, int]) -> None:
        self.viewports.append(viewport)

    def goto(self, url: str) -> None:
        self.gotos.append(url)

    def wait_for_selector(self, selector: str) -> None:
        self.waits.append(("selector", selector))

    def wait_for_load_state(self, state: str) -> None:
        self.waits.append(("load_state", state))

    def screenshot(self, *, path: str, full_page: bool = False) -> None:
        Path(path).write_text(f"full_page={full_page}", encoding="utf-8")
        self.screenshots.append(("page", path))

    def locator(self, selector: str) -> _FakeLocator:
        return _FakeLocator(self, selector)


def test_capture_live_visualizer_and_federate_service_additive(tmp_path: Path) -> None:
    page = _FakePage(
        counts={
            "#objects-list .list-row[data-index]": 1,
            "#fom-detail .tree-toggle-button": 1,
            "#plugin-root": 1,
        }
    )
    visualizer_captures = _capture_live_visualizer(
        page,
        tmp_path,
        base_url="http://127.0.0.1:9000/",
    )
    federate_service_captures = _capture_live_federate_service(
        page,
        tmp_path,
        base_url="http://127.0.0.1:9100",
    )

    assert page.gotos[0] == "http://127.0.0.1:9000"
    assert page.gotos[1] == "http://127.0.0.1:9100/docs"
    assert ("selector", "#fom-detail") in page.waits
    assert ("load_state", "networkidle") in page.waits
    assert any(capture["image_rel"] == "live-visualizer-overview.png" for capture in visualizer_captures)
    assert any(capture["image_rel"] == "live-visualizer-plugin-panel.png" for capture in visualizer_captures)
    assert federate_service_captures == [
        {
            "title": "Live Federate Service Contract Docs",
            "description": "Swagger-backed live capture from an already running federate-service surface.",
            "image_rel": "live-federate-service-docs.png",
            "source": "http://127.0.0.1:9100/docs",
        }
    ]
