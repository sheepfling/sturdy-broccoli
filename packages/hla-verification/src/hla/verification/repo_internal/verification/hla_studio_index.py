"""Shared HLA Studio aggregate index helpers."""
from __future__ import annotations

from dataclasses import dataclass
import html
import os
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class StudioSurfaceLink:
    name: str
    href: str
    summary: str
    alias: str
    command: str


@dataclass(frozen=True)
class StudioArtifactLink:
    label: str
    href: str
    description: str
    group: str = "Generated artifacts"


def _surface_card(link: StudioSurfaceLink) -> str:
    return f"""
    <article class="surface-card">
      <div class="kicker">HLA Studio Surface</div>
      <h2>{html.escape(link.name)}</h2>
      <p>{html.escape(link.summary)}</p>
      <div class="meta">alias: <code>{html.escape(link.alias)}</code></div>
      <div class="meta">launch: <code>{html.escape(link.command)}</code></div>
      <p><a href="{html.escape(link.href)}">Open surface</a></p>
    </article>
    """


def _artifact_card(link: StudioArtifactLink) -> str:
    return f"""
    <article class="artifact-card">
      <div class="kicker">{html.escape(link.group)}</div>
      <h2>{html.escape(link.label)}</h2>
      <p>{html.escape(link.description)}</p>
      <p><a href="{html.escape(link.href)}">Open artifact</a></p>
    </article>
    """


def render_hla_studio_index_html(
    *,
    surfaces: Iterable[StudioSurfaceLink],
    artifacts: Iterable[StudioArtifactLink],
) -> str:
    surface_cards = "\n".join(_surface_card(link) for link in surfaces)
    artifact_cards = "\n".join(_artifact_card(link) for link in artifacts)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>HLA Studio</title>
  <style>
    :root {{
      --bg: linear-gradient(180deg, #f6f0e3, #ebe7dc 58%, #dce8e7);
      --panel: rgba(255,255,255,0.88);
      --line: rgba(25,35,45,0.10);
      --ink: #17232d;
      --muted: #5d6b75;
      --accent: #0f6a73;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font: 15px/1.55 "IBM Plex Sans", "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }}
    main {{ max-width: 1440px; margin: 0 auto; padding: 28px; }}
    .hero, .surface-card, .artifact-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: 0 16px 38px rgba(18,32,43,0.06);
    }}
    .hero {{ padding: 24px; margin-bottom: 20px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 18px; }}
    .surface-card, .artifact-card {{ padding: 18px; }}
    .kicker {{
      font-size: 0.78rem;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 8px;
    }}
    h1, h2 {{ margin-top: 0; }}
    code {{
      background: rgba(15,106,115,0.08);
      border-radius: 6px;
      padding: 2px 6px;
    }}
    .meta {{ color: var(--muted); margin-bottom: 8px; }}
    a {{ color: var(--accent); text-decoration: none; font-weight: 600; }}
    a:hover {{ text-decoration: underline; }}
    .section-head {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 12px;
      margin: 24px 0 12px;
    }}
    .section-note {{ color: var(--muted); }}
    @media (max-width: 720px) {{
      main {{ padding: 18px 14px 28px; }}
      .section-head {{ display: block; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="kicker">HLA Studio Surfaces</div>
      <h1>HLA Studio</h1>
      <p>One index for the three operator-facing browser and API surfaces: FOM Explorer, Federation Visualizer, and RTI Bridge API.</p>
      <p>Use this page to jump into the live surfaces and the generated artifact packets that exercise them.</p>
    </section>

    <div class="section-head">
      <h2>Surfaces</h2>
      <div class="section-note">Preferred operator names with launch aliases preserved</div>
    </div>
    <section class="grid">
      {surface_cards}
    </section>

    <div class="section-head">
      <h2>Artifacts</h2>
      <div class="section-note">Generated packets, snapshots, and contract exports when present</div>
    </div>
    <section class="grid">
      {artifact_cards}
    </section>
  </main>
</body>
</html>
"""


def relative_href(*, from_dir: Path, target: Path) -> str:
    return os.path.relpath(target, from_dir).replace(os.sep, "/")


def write_hla_studio_index(
    output_dir: str | Path,
    *,
    surfaces: Iterable[StudioSurfaceLink],
    artifacts: Iterable[StudioArtifactLink],
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    path = output_path / "index.html"
    path.write_text(
        render_hla_studio_index_html(surfaces=tuple(surfaces), artifacts=tuple(artifacts)),
        encoding="utf-8",
    )
    return path


__all__ = [
    "StudioArtifactLink",
    "StudioSurfaceLink",
    "relative_href",
    "render_hla_studio_index_html",
    "write_hla_studio_index",
]
