"""Reusable browser capture helpers for repo UI surfaces."""
from __future__ import annotations

import contextlib
import html
import json
import socket
import threading
import time
from pathlib import Path
from typing import Any


def launch_browser() -> tuple[Any, Any, str]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - operator dependency guard
        raise SystemExit("playwright is required; install repo Python dependencies and run `playwright install`.") from exc

    errors: list[str] = []
    manager = sync_playwright()
    pw = manager.start()
    for browser_type_name in ("chromium", "webkit", "firefox"):
        browser_type = getattr(pw, browser_type_name)
        try:
            browser = browser_type.launch(headless=True)
            return pw, browser, browser_type_name
        except Exception as exc:  # pragma: no cover - env dependent
            errors.append(f"{browser_type_name}: {exc}")
    pw.stop()
    raise SystemExit("Playwright browser launch failed: " + " | ".join(errors))


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.bind(("127.0.0.1", 0))
        return int(handle.getsockname()[1])


@contextlib.contextmanager
def run_local_app(app: Any, *, host: str = "127.0.0.1"):
    import uvicorn  # pyright: ignore[reportMissingImports]

    port = find_free_port()
    config = uvicorn.Config(app, host=host, port=port, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.time() + 10.0
    while not getattr(server, "started", False):
        if time.time() > deadline:
            raise RuntimeError("Timed out waiting for local uvicorn app to start.")
        time.sleep(0.05)
    try:
        yield f"http://{host}:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=5.0)


def write_gallery_index(output_dir: Path, *, browser_name: str, captures: list[dict[str, str]]) -> Path:
    cards = "\n".join(
        f"""
        <article class="card">
          <h2>{html.escape(item['title'])}</h2>
          <p>{html.escape(item['description'])}</p>
          <a href="{html.escape(item['image_rel'])}"><img src="{html.escape(item['image_rel'])}" alt="{html.escape(item['title'])}"></a>
          <div class="meta">source: <code>{html.escape(item['source'])}</code></div>
        </article>
        """
        for item in captures
    )
    content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>UI Surface Screenshot Packet</title>
  <style>
    body {{ font: 15px/1.5 "Avenir Next", "Segoe UI", sans-serif; margin: 0; color: #19232d; background: linear-gradient(180deg, #f4efe7, #ece5d8); }}
    main {{ max-width: 1440px; margin: 0 auto; padding: 24px; }}
    .hero {{ background: rgba(255,255,255,0.8); border: 1px solid rgba(0,0,0,0.08); border-radius: 18px; padding: 20px; margin-bottom: 18px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 18px; }}
    .card {{ background: rgba(255,255,255,0.88); border: 1px solid rgba(0,0,0,0.08); border-radius: 18px; padding: 16px; }}
    img {{ width: 100%; border-radius: 12px; border: 1px solid rgba(0,0,0,0.1); }}
    code {{ background: rgba(0,0,0,0.05); padding: 2px 6px; border-radius: 6px; }}
    .meta {{ color: #5a6976; margin-top: 10px; }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <h1>UI Surface Screenshot Packet</h1>
      <p>Deterministic browser captures for the FOM workbench, federation visualizer, and federate-service contract surface.</p>
      <p>Browser: <code>{html.escape(browser_name)}</code></p>
      <p>Regenerate: <code>./tools/ui-surface-screenshots</code></p>
    </section>
    <section class="grid">
      {cards}
    </section>
  </main>
</body>
</html>
"""
    path = output_dir / "index.html"
    path.write_text(content, encoding="utf-8")
    return path


def write_gallery_manifest(
    output_dir: Path,
    *,
    browser_name: str,
    captures: list[dict[str, str]],
    index_path: Path,
) -> Path:
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "browser": browser_name,
                "captures": captures,
                "index_html": str(index_path),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest_path


def normalize_docs_url(url: str) -> str:
    normalized = url.rstrip("/")
    if normalized.endswith("/docs"):
        return normalized
    return f"{normalized}/docs"


def capture_live_visualizer(page: Any, output_dir: Path, *, base_url: str, prefix: str = "live") -> list[dict[str, str]]:
    normalized_base_url = base_url.rstrip("/")
    captures: list[dict[str, str]] = []
    page.set_viewport_size({"width": 1720, "height": 1320})
    page.goto(normalized_base_url)
    page.wait_for_selector("#fom-detail")
    overview_path = output_dir / f"{prefix}-visualizer-overview.png"
    page.screenshot(path=str(overview_path), full_page=True)
    captures.append(
        {
            "title": "Live Federation Visualizer Overview",
            "description": "Live capture from an already running federation visualizer surface.",
            "image_rel": overview_path.name,
            "source": f"{normalized_base_url}/",
        }
    )
    object_rows = page.locator("#objects-list .list-row[data-index]")
    if object_rows.count() > 0:
        object_rows.first.click()
        object_pin_path = output_dir / f"{prefix}-visualizer-object-pin.png"
        page.locator("#object-detail").screenshot(path=str(object_pin_path))
        captures.append(
            {
                "title": "Live Federation Visualizer Object Pin",
                "description": "Pinned object detail captured from the live visualizer surface.",
                "image_rel": object_pin_path.name,
                "source": f"{normalized_base_url}/",
            }
        )
    tree_toggles = page.locator("#fom-detail .tree-toggle-button")
    if tree_toggles.count() > 0:
        tree_toggles.first.click()
    fom_panel_path = output_dir / f"{prefix}-visualizer-fom-panel.png"
    page.locator("#fom-detail").screenshot(path=str(fom_panel_path))
    captures.append(
        {
            "title": "Live Federation Visualizer FOM Tree",
            "description": "FOM tree panel captured from the live visualizer surface.",
            "image_rel": fom_panel_path.name,
            "source": f"{normalized_base_url}/",
        }
    )
    plugin_root = page.locator("#plugin-root")
    if plugin_root.count() > 0:
        plugin_path = output_dir / f"{prefix}-visualizer-plugin-panel.png"
        plugin_root.screenshot(path=str(plugin_path))
        captures.append(
            {
                "title": "Live Federation Visualizer Semantic Panel",
                "description": "Scenario plugin panel captured from the live visualizer surface when present.",
                "image_rel": plugin_path.name,
                "source": f"{normalized_base_url}/",
            }
        )
    return captures


def capture_live_federate_service(page: Any, output_dir: Path, *, base_url: str, prefix: str = "live") -> list[dict[str, str]]:
    docs_url = normalize_docs_url(base_url)
    captures: list[dict[str, str]] = []
    page.set_viewport_size({"width": 1600, "height": 1200})
    page.goto(docs_url)
    page.wait_for_load_state("networkidle")
    docs_path = output_dir / f"{prefix}-federate-service-docs.png"
    page.screenshot(path=str(docs_path), full_page=True)
    captures.append(
        {
            "title": "Live Federate Service Contract Docs",
            "description": "Swagger-backed live capture from an already running federate-service surface.",
            "image_rel": docs_path.name,
            "source": docs_url,
        }
    )
    return captures


__all__ = [
    "capture_live_federate_service",
    "capture_live_visualizer",
    "find_free_port",
    "launch_browser",
    "normalize_docs_url",
    "run_local_app",
    "write_gallery_index",
    "write_gallery_manifest",
]
