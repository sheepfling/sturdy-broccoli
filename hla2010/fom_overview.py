"""Reusable utilities for summarizing FOM/MIM catalogs.

The report intentionally trades raw XML completeness for readability:

- inheritance tree
- declared vs total members
- module provenance
- optional Mermaid diagrams for small hierarchies

The Target/Radar FOM is the default example use case, but the helpers work for
any resolved FOM/MIM catalog returned by :class:`hla2010.fom.FOMResolver`.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from .fom import FOMModule, FOMResolver


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "analysis" / "fom_overview"


@dataclass(frozen=True)
class FOMNodeRow:
    kind: str
    full_name: str
    parent_name: str | None
    declared_count: int
    total_count: int
    origin_modules: tuple[str, ...]
    declared_names: tuple[str, ...]
    total_names: tuple[str, ...]
    datatype_hints: tuple[str, ...]


@dataclass(frozen=True)
class FOMOverviewReport:
    title: str
    sources: tuple[str, ...]
    include_standard_mim: bool
    merged_summary: dict[str, Any]
    object_rows: tuple[FOMNodeRow, ...]
    interaction_rows: tuple[FOMNodeRow, ...]
    dimensions: tuple[str, ...]
    mermaid_objects: str | None = None
    mermaid_interactions: str | None = None

    def to_json(self) -> str:
        return json.dumps(
            {
                "title": self.title,
                "sources": list(self.sources),
                "include_standard_mim": self.include_standard_mim,
                "merged_summary": self.merged_summary,
                "dimensions": list(self.dimensions),
                "object_rows": [asdict(row) for row in self.object_rows],
                "interaction_rows": [asdict(row) for row in self.interaction_rows],
                "mermaid_objects": self.mermaid_objects,
                "mermaid_interactions": self.mermaid_interactions,
            },
            indent=2,
            sort_keys=True,
        )


def _slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", text.strip()).strip("-").lower()
    return slug or "fom-overview"


def _anchor_slug(text: str) -> str:
    return _slugify(text).replace("-", "_")


def _html_escape(text: Any) -> str:
    return html.escape("" if text is None else str(text), quote=True)


def _source_label(source: Any) -> str:
    if isinstance(source, FOMModule):
        if source.name:
            return source.name
        if source.path is not None:
            return source.path.name
        return str(source.source)
    path = Path(str(source))
    return path.name if path.name else str(source)


def _origin_map(modules: Iterable[FOMModule]) -> dict[str, tuple[str, ...]]:
    origins: dict[str, list[str]] = defaultdict(list)
    for module in modules:
        label = _source_label(module)
        for spec in module.object_classes:
            if label not in origins[spec.full_name]:
                origins[spec.full_name].append(label)
        for spec in module.interaction_classes:
            if label not in origins[spec.full_name]:
                origins[spec.full_name].append(label)
    return {key: tuple(values) for key, values in origins.items()}


def _datatype_hints(spec: Any) -> tuple[str, ...]:
    hints: list[str] = []
    datatype_map = getattr(spec, "attribute_datatypes", None) or getattr(spec, "parameter_datatypes", None) or {}
    for value in datatype_map.values():
        if value and value not in hints:
            hints.append(value)
    return tuple(hints)


def _build_rows(kind: str, specs: Iterable[Any], origins: dict[str, tuple[str, ...]]) -> tuple[FOMNodeRow, ...]:
    rows: list[FOMNodeRow] = []
    for spec in sorted(specs, key=lambda item: item.full_name):
        declared_names = tuple(getattr(spec, "declared_attributes", ()) or getattr(spec, "declared_parameters", ()))
        total_names = tuple(getattr(spec, "attributes", ()) or getattr(spec, "parameters", ()))
        rows.append(
            FOMNodeRow(
                kind=kind,
                full_name=spec.full_name,
                parent_name=spec.parent_name,
                declared_count=len(declared_names),
                total_count=len(total_names),
                origin_modules=origins.get(spec.full_name, ()),
                declared_names=declared_names,
                total_names=total_names,
                datatype_hints=_datatype_hints(spec),
            )
        )
    return tuple(rows)


def _tree_lines(rows: Iterable[FOMNodeRow], kind: str) -> list[str]:
    row_map = {row.full_name: row for row in rows}
    children: dict[str | None, list[FOMNodeRow]] = defaultdict(list)
    for row in rows:
        children[row.parent_name].append(row)
    for bucket in children.values():
        bucket.sort(key=lambda row: row.full_name)

    lines: list[str] = [f"## {kind} Tree", ""]

    def render(node: FOMNodeRow, depth: int = 0) -> None:
        indent = "  " * depth
        descriptor = f"{node.full_name} ({node.declared_count}/{node.total_count})"
        if node.origin_modules:
            descriptor += f" [{', '.join(node.origin_modules)}]"
        lines.append(f"{indent}- {descriptor}")
        for child in children.get(node.full_name, ()):
            render(child, depth + 1)

    roots = [row for row in rows if row.parent_name not in row_map]
    for root in roots:
        render(root)
    lines.append("")
    return lines


def _mermaid_graph(rows: Iterable[FOMNodeRow]) -> str | None:
    rows = tuple(rows)
    if len(rows) > 40:
        return None
    row_map = {row.full_name: idx for idx, row in enumerate(rows)}
    lines = ["flowchart TD"]
    for idx, row in enumerate(rows):
        node_id = f"n{idx}"
        label = row.full_name.replace('"', "'")
        lines.append(f'  {node_id}["{label}"]')
    for idx, row in enumerate(rows):
        if row.parent_name and row.parent_name in row_map:
            parent_id = f"n{row_map[row.parent_name]}"
            lines.append(f"  {parent_id} --> n{idx}")
    return "\n".join(lines)


def _detail_lines(rows: Iterable[FOMNodeRow], title: str, *, item_label: str) -> list[str]:
    lines = [f"## {title}", ""]
    for row in rows:
        if row.total_count > 8:
            continue
        lines.append(f"<details><summary>{row.full_name} ({row.declared_count}/{row.total_count})</summary>")
        lines.append("")
        lines.append(f"- Parent: `{row.parent_name or ''}`")
        lines.append(f"- Origins: {', '.join(row.origin_modules) or 'n/a'}")
        if item_label == "attribute":
            lines.append(f"- Declared attributes: {', '.join(row.declared_names) or 'n/a'}")
            lines.append(f"- Available attributes: {', '.join(row.total_names) or 'n/a'}")
        else:
            lines.append(f"- Declared parameters: {', '.join(row.declared_names) or 'n/a'}")
            lines.append(f"- Available parameters: {', '.join(row.total_names) or 'n/a'}")
        if row.datatype_hints:
            lines.append(f"- Datatype hints: {', '.join(row.datatype_hints)}")
        lines.append("")
        lines.append("</details>")
        lines.append("")
    return lines


def _render_markdown(report: FOMOverviewReport) -> str:
    lines = [
        f"# {report.title}",
        "",
        "This overview emphasizes inheritance, declared-vs-available members, and module provenance so the active FOM is easier to read than raw XML.",
        "",
        "## Summary",
        "",
        f"- Sources: {', '.join(report.sources) or 'n/a'}",
        f"- Standard MIM included: {'yes' if report.include_standard_mim else 'no'}",
        f"- Logical time implementation: {report.merged_summary.get('logical_time_implementation') or 'n/a'}",
        f"- Object classes: {len(report.object_rows)}",
        f"- Interaction classes: {len(report.interaction_rows)}",
        f"- Dimensions: {len(report.dimensions)}",
        "",
        "## Module View",
        "",
        "| Kind | Name | Parent | Declared | Available | Origins |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in report.object_rows:
        lines.append(
            f"| object | {row.full_name} | {row.parent_name or ''} | {row.declared_count} | {row.total_count} | {', '.join(row.origin_modules) or ''} |"
        )
    for row in report.interaction_rows:
        lines.append(
            f"| interaction | {row.full_name} | {row.parent_name or ''} | {row.declared_count} | {row.total_count} | {', '.join(row.origin_modules) or ''} |"
        )
    lines.append("")
    lines.extend(_tree_lines(report.object_rows, "Object Classes"))
    if report.mermaid_objects:
        lines.extend(["```mermaid", report.mermaid_objects, "```", ""])
    lines.extend(_tree_lines(report.interaction_rows, "Interaction Classes"))
    if report.mermaid_interactions:
        lines.extend(["```mermaid", report.mermaid_interactions, "```", ""])
    lines.extend(_detail_lines(report.object_rows, "Object Class Details", item_label="attribute"))
    lines.extend(_detail_lines(report.interaction_rows, "Interaction Class Details", item_label="parameter"))
    lines.extend(
        [
            "## Dimensions",
            "",
            "| Name |",
            "|---|",
        ]
    )
    for dimension in report.dimensions:
        lines.append(f"| {dimension} |")
    lines.append("")
    return "\n".join(lines)


def _render_tree_html(rows: Iterable[FOMNodeRow]) -> str:
    rows = tuple(rows)
    row_map = {row.full_name: row for row in rows}
    children: dict[str | None, list[FOMNodeRow]] = defaultdict(list)
    for row in rows:
        children[row.parent_name].append(row)
    for bucket in children.values():
        bucket.sort(key=lambda row: row.full_name)

    def render_node(node: FOMNodeRow) -> str:
        origin_text = ", ".join(node.origin_modules) or "n/a"
        meta = f"{node.declared_count}/{node.total_count}"
        child_nodes = children.get(node.full_name, ())
        child_html = ""
        if child_nodes:
            child_html = "<ul>" + "".join(render_node(child) for child in child_nodes) + "</ul>"
        return (
            f'<li id="{_anchor_slug(node.kind + "-" + node.full_name)}" data-search="{_html_escape(node.full_name + " " + origin_text)}">'
            f'<span class="node-name">{_html_escape(node.full_name)}</span> '
            f'<span class="node-meta">({meta})</span> '
            f'<span class="node-origin">[{_html_escape(origin_text)}]</span>'
            f"{child_html}"
            "</li>"
        )

    roots = [row for row in rows if row.parent_name not in row_map]
    if not roots:
        return '<p class="muted">No hierarchy nodes available.</p>'
    return '<ul class="tree">' + "".join(render_node(root) for root in roots) + "</ul>"


def _render_detail_html(rows: Iterable[FOMNodeRow], *, item_label: str) -> str:
    parts: list[str] = []
    for row in rows:
        if row.total_count > 8:
            continue
        detail_search = " ".join(
            (
                row.full_name,
                row.parent_name or "",
                " ".join(row.origin_modules),
                " ".join(row.declared_names),
                " ".join(row.total_names),
                " ".join(row.datatype_hints),
            )
        )
        details: list[str] = [
            f'<details class="class-detail" id="{_anchor_slug(row.kind + "-detail-" + row.full_name)}" data-search="{_html_escape(detail_search)}">',
            (
                "<summary>"
                f'<span class="node-name">{_html_escape(row.full_name)}</span> '
                f'<span class="node-meta">({row.declared_count}/{row.total_count})</span>'
                "</summary>"
            ),
            '<dl class="detail-grid">',
            f"<dt>Parent</dt><dd>{_html_escape(row.parent_name or 'n/a')}</dd>",
            f"<dt>Origins</dt><dd>{_html_escape(', '.join(row.origin_modules) or 'n/a')}</dd>",
        ]
        if item_label == "attribute":
            details.extend(
                [
                    f"<dt>Declared attributes</dt><dd>{_html_escape(', '.join(row.declared_names) or 'n/a')}</dd>",
                    f"<dt>Available attributes</dt><dd>{_html_escape(', '.join(row.total_names) or 'n/a')}</dd>",
                ]
            )
        else:
            details.extend(
                [
                    f"<dt>Declared parameters</dt><dd>{_html_escape(', '.join(row.declared_names) or 'n/a')}</dd>",
                    f"<dt>Available parameters</dt><dd>{_html_escape(', '.join(row.total_names) or 'n/a')}</dd>",
                ]
            )
        if row.datatype_hints:
            details.append(f"<dt>Datatype hints</dt><dd>{_html_escape(', '.join(row.datatype_hints))}</dd>")
        details.extend(["</dl>", "</details>"])
        parts.append("\n".join(details))
    return "\n".join(parts) if parts else '<p class="muted">No compact detail rows available.</p>'


def _render_mermaid_html(source: str | None) -> str:
    if not source:
        return '<p class="muted">Not generated for this catalog size.</p>'
    return f'<pre class="mermaid-source">{_html_escape(source)}</pre>'


def _report_search_index(report: FOMOverviewReport) -> list[dict[str, Any]]:
    lookup = {
        "object": {row.full_name: row for row in report.object_rows},
        "interaction": {row.full_name: row for row in report.interaction_rows},
    }
    child_counts = {
        "object": defaultdict(int),
        "interaction": defaultdict(int),
    }
    for row in report.object_rows:
        if row.parent_name:
            child_counts["object"][row.parent_name] += 1
    for row in report.interaction_rows:
        if row.parent_name:
            child_counts["interaction"][row.parent_name] += 1

    def lineage(kind: str, name: str) -> list[str]:
        chain: list[str] = []
        current = lookup[kind].get(name)
        while current is not None:
            chain.append(current.full_name)
            current = lookup[kind].get(current.parent_name or "")
        chain.reverse()
        return chain

    items: list[dict[str, Any]] = []
    for row in report.object_rows:
        items.append(
            {
                "kind": "object",
                "name": row.full_name,
                "anchor": _anchor_slug("object-" + row.full_name),
                "detail_anchor": _anchor_slug("object-detail-" + row.full_name),
                "parent": row.parent_name or "",
                "origin_modules": list(row.origin_modules),
                "lineage": lineage("object", row.full_name),
                "leaf": child_counts["object"].get(row.full_name, 0) == 0,
            }
        )
    for row in report.interaction_rows:
        items.append(
            {
                "kind": "interaction",
                "name": row.full_name,
                "anchor": _anchor_slug("interaction-" + row.full_name),
                "detail_anchor": _anchor_slug("interaction-detail-" + row.full_name),
                "parent": row.parent_name or "",
                "origin_modules": list(row.origin_modules),
                "lineage": lineage("interaction", row.full_name),
                "leaf": child_counts["interaction"].get(row.full_name, 0) == 0,
            }
        )
    return items


def _render_report_index_html(report: FOMOverviewReport, html_filename: str) -> str:
    items = _report_search_index(report)
    object_items = [item for item in items if item["kind"] == "object"]
    interaction_items = [item for item in items if item["kind"] == "interaction"]
    artifact_prefix = _slugify(report.title)
    artifact_html_name = f"{artifact_prefix}.html"
    artifact_md_name = f"{artifact_prefix}.md"
    artifact_json_name = f"{artifact_prefix}.json"
    summary_line = f"{len(report.object_rows)} object classes, {len(report.interaction_rows)} interaction classes, {len(report.dimensions)} dimensions"
    artifact_meta_html = (
        f'<span class="pill">{_html_escape(artifact_html_name)}</span>'
        f'<span class="pill">{_html_escape(artifact_md_name)}</span>'
        f'<span class="pill">{_html_escape(artifact_json_name)}</span>'
    )
    source_summary = ", ".join(report.sources) or "n/a"
    logical_time_summary = report.merged_summary.get("logical_time_implementation") or "n/a"

    def render_group(items: list[dict[str, Any]], kind: str) -> str:
        def render_item(item: dict[str, Any]) -> str:
            leaf_tag = ' <span class="pill">leaf</span>' if item["leaf"] else ""
            search_data = " ".join(
                (
                    item["name"],
                    item["kind"],
                    item["parent"],
                    " ".join(item["origin_modules"]),
                    " ".join(item["lineage"]),
                )
            )
            return (
                f'<li data-kind="{_html_escape(kind)}" '
                f'data-leaf="{_html_escape("true" if item["leaf"] else "false")}" '
                f'data-search="{_html_escape(search_data)}" '
                f'data-anchor="{_html_escape(html_filename + "#" + item["detail_anchor"])}" '
                f'data-lineage="{_html_escape(" > ".join(item["lineage"]))}" '
                f'data-name="{_html_escape(item["name"])}" '
                f'data-origin="{_html_escape(", ".join(item["origin_modules"]) or "n/a")}" '
                'onclick="setDetails(this)">'
                f'<a href="{_html_escape(html_filename)}#{_html_escape(item["detail_anchor"])}">'
                f"{_html_escape(item['name'])}</a> "
                f'<span class="muted">({_html_escape(item["kind"])})</span>'
                f"{leaf_tag}"
                "</li>"
            )

        item_rows = "\n".join(render_item(item) for item in items)
        label = "Object" if kind == "object" else "Interaction"
        return f"""
        <div class="card">
          <h2>{label} Classes</h2>
          <input type="search" placeholder="Filter {label.lower()} classes..." oninput="filterKind('{kind}', this.value)">
          <label style="display:block; margin:-6px 0 10px; color: #9ca3af; font-size: .92rem;">
            <input type="checkbox" onchange="toggleLeaves('{kind}', this.checked)">
            Show only leaf nodes
          </label>
          <ul id="{kind}-list">
            {item_rows}
          </ul>
        </div>
        """

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{_html_escape(report.title)} | FOM Index</title>
  <style>
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0f172a;
      color: #e5e7eb;
    }}
    .wrap {{ max-width: 1000px; margin: 0 auto; padding: 24px; }}
    section {{
      background: rgba(17, 24, 39, .9);
      border: 1px solid #334155;
      border-radius: 18px;
      padding: 20px;
      margin-bottom: 18px;
    }}
    input[type=\"search\"] {{
      width: 100%;
      padding: 14px 16px;
      border-radius: 12px;
      border: 1px solid #334155;
      background: #111827;
      color: #e5e7eb;
      font-size: 1rem;
      margin: 14px 0 18px;
    }}
    ul {{ margin: 0; padding-left: 20px; }}
    li {{ margin: 6px 0; }}
    a {{ color: #7dd3fc; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .meta {{ color: #9ca3af; }}
    .muted {{ color: #9ca3af; }}
    .pill {{
      display: inline-block;
      padding: 2px 10px;
      border-radius: 999px;
      border: 1px solid rgba(125,211,252,.25);
      background: rgba(125,211,252,.12);
      color: #dbeafe;
      margin-right: 6px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 12px;
      margin-top: 12px;
    }}
    .card {{
      background: #111827;
      border: 1px solid #334155;
      border-radius: 14px;
      padding: 14px;
    }}
    .card h2 {{ margin-top: 0; font-size: 1rem; }}
    .nav-panel {{
      background: #111827;
      border: 1px solid #334155;
      border-radius: 14px;
      padding: 14px;
      margin-top: 14px;
    }}
    .nav-panel h3 {{ margin-top: 0; }}
    .breadcrumb {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
      margin: 8px 0 0;
    }}
    .breadcrumb a {{
      color: #7dd3fc;
      text-decoration: none;
      border-bottom: 1px solid rgba(125,211,252,.3);
    }}
    .breadcrumb a:hover {{ text-decoration: underline; }}
    .breadcrumb .pill {{ margin-bottom: 0; }}
    #object-list li, #interaction-list li {{
      cursor: pointer;
    }}
    .detail-toggle {{
      margin-top: 14px;
      border-top: 1px dashed #334155;
      padding-top: 12px;
    }}
    .detail-toggle summary {{
      cursor: pointer;
      color: #dbeafe;
      font-weight: 600;
    }}
    .hidden {{
      display: none !important;
    }}
  </style>
  <script>
    function filterKind(kind, value) {{
      const q = value.trim().toLowerCase();
      document.querySelectorAll('#' + kind + '-list [data-search]').forEach((el) => {{
        const text = (el.getAttribute('data-search') || '').toLowerCase();
        el.style.display = !q || text.includes(q) ? '' : 'none';
      }});
    }}
    function toggleLeaves(kind, onlyLeaves) {{
      document.querySelectorAll('#' + kind + '-list li[data-leaf]').forEach((el) => {{
        if (!onlyLeaves) {{
          el.classList.remove('hidden');
          return;
        }}
        el.classList.toggle('hidden', el.getAttribute('data-leaf') !== 'true');
      }});
    }}
    function setDetails(el) {{
      const panel = document.getElementById('ancestor-panel');
      const title = el.getAttribute('data-name') || 'n/a';
      const kind = el.getAttribute('data-kind') || 'n/a';
      const anchor = el.getAttribute('data-anchor') || '#';
      const lineage = (el.getAttribute('data-lineage') || '').split(' > ').filter(Boolean);
      const origin = el.getAttribute('data-origin') || 'n/a';
      const ancestorHtml = lineage.length
        ? '<div class="breadcrumb">' + lineage.map((item) => '<span class="pill">' + item + '</span>').join('') + '</div>'
        : '<p class="muted">No ancestors recorded.</p>';
      panel.innerHTML = '<h3>' + title + '</h3>'
        + '<p class="muted">' + kind + '</p>'
        + '<p><a href="' + anchor + '">Open detail section</a></p>'
        + '<p class="muted">Origins: ' + origin + '</p>'
        + '<p class="muted">Ancestors:</p>'
        + ancestorHtml;
      if (location.hash !== anchor.split('#').pop()) {{
        history.replaceState(null, '', anchor);
      }}
    }}
    window.addEventListener('DOMContentLoaded', () => {{
      if (location.hash) {{
        const target = document.getElementById(location.hash.slice(1));
        if (target && target.matches('li[data-kind]')) {{
          setDetails(target);
        }}
      }}
    }});
  </script>
</head>
<body>
  <div class=\"wrap\">
    <section>
      <h1>{_html_escape(report.title)} index</h1>
      <p class=\"meta\">Artifacts: {artifact_meta_html}</p>
      <p>This index is a fast navigation layer over the rendered overview. Use the separate filters to narrow object and interaction classes independently.</p>
      <div class=\"grid\">
        <div class=\"card\"><h2>Summary</h2><p>{_html_escape(summary_line)}</p></div>
        <div class=\"card\"><h2>Open report</h2><p><a href=\"{_html_escape(html_filename)}\">{_html_escape(html_filename)}</a></p></div>
        <div class=\"card\"><h2>Search help</h2><p>Click a class to preview its ancestry, then open the report anchor for the full detail block.</p></div>
      </div>
      <details class=\"detail-toggle\" open>
        <summary>Selected class provenance</summary>
        <div class=\"nav-panel\">
          <h3>Selected class</h3>
          <div id=\"ancestor-panel\">
            <p class=\"muted\">Click any class in the lists below to inspect its ancestor chain.</p>
          </div>
        </div>
      </details>
    </section>
    <section>
      <h2>Classes</h2>
      <div class=\"grid\">
        {render_group(object_items, "object")}
        {render_group(interaction_items, "interaction")}
      </div>
    </section>
  </div>
</body>
</html>
"""


def _render_html(report: FOMOverviewReport) -> str:
    module_rows = [
        (
            "object",
            row.full_name,
            row.parent_name or "",
            row.declared_count,
            row.total_count,
            ", ".join(row.origin_modules),
        )
        for row in report.object_rows
    ] + [
        (
            "interaction",
            row.full_name,
            row.parent_name or "",
            row.declared_count,
            row.total_count,
            ", ".join(row.origin_modules),
        )
        for row in report.interaction_rows
    ]
    module_rows.sort(key=lambda item: (item[0], item[1]))
    source_summary = ", ".join(report.sources) or "n/a"
    logical_time_summary = report.merged_summary.get("logical_time_implementation") or "n/a"
    summary_cards = "\n".join(
        [
            (f'<div class="card"><div class="label">Sources</div><div class="value" style="font-size:1rem">{_html_escape(source_summary)}</div></div>'),
            (f'<div class="card"><div class="label">Standard MIM</div><div class="value">{"yes" if report.include_standard_mim else "no"}</div></div>'),
            (
                '<div class="card"><div class="label">Logical time</div>'
                f'<div class="value" style="font-size:1rem">{_html_escape(logical_time_summary)}</div></div>'
            ),
            f'<div class="card"><div class="label">Object classes</div><div class="value">{len(report.object_rows)}</div></div>',
            f'<div class="card"><div class="label">Interaction classes</div><div class="value">{len(report.interaction_rows)}</div></div>',
            f'<div class="card"><div class="label">Dimensions</div><div class="value">{len(report.dimensions)}</div></div>',
        ]
    )

    module_table_rows = "\n".join(
        (
            "<tr>"
            f"<td>{_html_escape(kind)}</td>"
            f"<td>{_html_escape(name)}</td>"
            f"<td>{_html_escape(parent)}</td>"
            f'<td class="num">{declared}</td>'
            f'<td class="num">{total}</td>'
            f"<td>{_html_escape(origins)}</td>"
            "</tr>"
        )
        for kind, name, parent, declared, total, origins in module_rows
    )

    dimensions = "\n".join(f"<li>{_html_escape(dimension)}</li>" for dimension in report.dimensions) or "<li>n/a</li>"

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{_html_escape(report.title)} | FOM Overview</title>
  <style>
    :root {{
      --bg: #0f172a;
      --panel: #111827;
      --panel-2: #1f2937;
      --text: #e5e7eb;
      --muted: #9ca3af;
      --accent: #7dd3fc;
      --accent-2: #a78bfa;
      --border: #334155;
      --code: #0b1120;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top, #1e293b 0, var(--bg) 45%);
      color: var(--text);
      line-height: 1.5;
    }}
    .wrap {{ max-width: 1320px; margin: 0 auto; padding: 24px; }}
    header {{
      background: linear-gradient(135deg, rgba(125,211,252,.12), rgba(167,139,250,.14));
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 24px;
      margin-bottom: 20px;
      box-shadow: 0 20px 60px rgba(15, 23, 42, .35);
    }}
    h1, h2, h3 {{ margin: 0 0 12px; line-height: 1.15; }}
    h1 {{ font-size: 2rem; }}
    h2 {{ margin-top: 28px; font-size: 1.25rem; }}
    p {{ margin: 0 0 12px; }}
    .muted {{ color: var(--muted); }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 12px;
      margin: 16px 0 0;
    }}
    .card {{
      background: rgba(17, 24, 39, .88);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
    }}
    .card .label {{ color: var(--muted); font-size: .8rem; text-transform: uppercase; letter-spacing: .08em; }}
    .card .value {{ font-size: 1.5rem; margin-top: 6px; font-weight: 700; }}
    section {{
      background: rgba(17, 24, 39, .82);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 20px;
      margin-bottom: 18px;
      overflow: hidden;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: .92rem;
    }}
    th, td {{
      border-bottom: 1px solid var(--border);
      padding: 8px 10px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: #bfdbfe;
      font-weight: 600;
      position: sticky;
      top: 0;
      background: rgba(17, 24, 39, .98);
      z-index: 1;
    }}
    td.num {{ text-align: right; white-space: nowrap; }}
    .scroll {{ overflow: auto; max-height: 70vh; border: 1px solid var(--border); border-radius: 14px; }}
    .tree {{
      padding-left: 18px;
      margin: 0;
    }}
    .tree li {{ margin: 6px 0; }}
    .node-name {{ color: #f8fafc; font-weight: 600; }}
    .node-meta {{ color: var(--accent); }}
    .node-origin {{ color: var(--muted); }}
    details.class-detail {{
      border: 1px solid var(--border);
      border-radius: 12px;
      margin: 10px 0;
      background: rgba(31, 41, 55, .7);
      overflow: hidden;
    }}
    details.class-detail > summary {{
      cursor: pointer;
      padding: 12px 14px;
      list-style: none;
      background: rgba(31, 41, 55, .9);
    }}
    details.class-detail > summary::-webkit-details-marker {{ display: none; }}
    .detail-grid {{
      display: grid;
      grid-template-columns: 220px 1fr;
      gap: 8px 12px;
      margin: 0;
      padding: 14px;
      border-top: 1px solid var(--border);
    }}
    .detail-grid dt {{ color: var(--accent-2); font-weight: 600; }}
    .detail-grid dd {{ margin: 0; color: var(--text); }}
    .pill {{
      display: inline-block;
      padding: 2px 10px;
      border-radius: 999px;
      background: rgba(125,211,252,.15);
      color: #dbeafe;
      border: 1px solid rgba(125,211,252,.25);
      margin-right: 6px;
      margin-bottom: 6px;
    }}
    pre.mermaid-source {{
      background: var(--code);
      border-radius: 14px;
      padding: 16px;
      overflow: auto;
      border: 1px solid var(--border);
      color: #dbeafe;
    }}
    ul.dimensions {{
      margin: 0;
      padding-left: 18px;
    }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <header>
      <h1>{_html_escape(report.title)}</h1>
      <p>This overview emphasizes inheritance, declared-vs-available members, and module provenance so the active FOM is easier to read than raw XML.</p>
      <div class=\"cards\">
        {summary_cards}
      </div>
    </header>

    <section>
      <h2>Module View</h2>
      <div class=\"scroll\">
        <table>
          <thead>
            <tr>
              <th>Kind</th>
              <th>Name</th>
              <th>Parent</th>
              <th>Declared</th>
              <th>Available</th>
              <th>Origins</th>
            </tr>
          </thead>
          <tbody>
            {module_table_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section>
      <h2>Object Classes Tree</h2>
      <p class=\"muted\">Search the index page to jump directly to a class detail block.</p>
      {_render_tree_html(report.object_rows)}
    </section>

    <section>
      <h2>Object Class Details</h2>
      {_render_detail_html(report.object_rows, item_label="attribute")}
    </section>

    <section>
      <h2>Interaction Classes Tree</h2>
      <p class=\"muted\">Search the index page to jump directly to a class detail block.</p>
      {_render_tree_html(report.interaction_rows)}
    </section>

    <section>
      <h2>Interaction Class Details</h2>
      {_render_detail_html(report.interaction_rows, item_label="parameter")}
    </section>

    <section>
      <h2>Mermaid Source</h2>
      <p class=\"muted\">The graph source is included here for portability. Small hierarchies can be rendered with Mermaid in an external viewer if desired.</p>
      <h3>Objects</h3>
      {_render_mermaid_html(report.mermaid_objects)}
      <h3>Interactions</h3>
      {_render_mermaid_html(report.mermaid_interactions)}
    </section>

    <section>
      <h2>Dimensions</h2>
      <ul class=\"dimensions\">
        {dimensions}
      </ul>
    </section>
  </div>
</body>
</html>
"""


def build_fom_overview(
    sources: Iterable[Any] | Any,
    *,
    include_standard_mim: bool = True,
    mim_source: Any | None = None,
    title: str | None = None,
) -> FOMOverviewReport:
    resolver = FOMResolver()
    modules = resolver.resolve_many(sources)
    mim = resolver.resolve(mim_source) if mim_source is not None else (resolver.resolve("HLAstandardMIM") if include_standard_mim else None)
    catalog = resolver.merge(sources, mim_source=mim_source, include_standard_mim=include_standard_mim)
    merged_modules = tuple([mim] if mim is not None else ()) + modules
    origin_map = _origin_map(merged_modules)
    object_rows = _build_rows("object", catalog.object_classes.values(), origin_map)
    interaction_rows = _build_rows("interaction", catalog.interaction_classes.values(), origin_map)
    report_title = title or (" + ".join(_source_label(module) for module in merged_modules) or "FOM overview")
    return FOMOverviewReport(
        title=report_title,
        sources=tuple(_source_label(module) for module in merged_modules),
        include_standard_mim=include_standard_mim,
        merged_summary=catalog.as_summary(),
        object_rows=object_rows,
        interaction_rows=interaction_rows,
        dimensions=tuple(sorted(catalog.dimensions)),
        mermaid_objects=_mermaid_graph(object_rows),
        mermaid_interactions=_mermaid_graph(interaction_rows),
    )


def write_fom_overview(
    sources: Iterable[Any] | Any,
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    include_standard_mim: bool = True,
    mim_source: Any | None = None,
    title: str | None = None,
) -> tuple[Path, Path]:
    report = build_fom_overview(
        sources,
        include_standard_mim=include_standard_mim,
        mim_source=mim_source,
        title=title,
    )
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    slug = _slugify(report.title)
    json_path = output_path / f"{slug}.json"
    md_path = output_path / f"{slug}.md"
    json_path.write_text(report.to_json(), encoding="utf-8")
    md_path.write_text(_render_markdown(report), encoding="utf-8")
    return json_path, md_path


def write_fom_overview_html(
    sources: Iterable[Any] | Any,
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    include_standard_mim: bool = True,
    mim_source: Any | None = None,
    title: str | None = None,
) -> Path:
    report = build_fom_overview(
        sources,
        include_standard_mim=include_standard_mim,
        mim_source=mim_source,
        title=title,
    )
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    slug = _slugify(report.title)
    html_path = output_path / f"{slug}.html"
    html_path.write_text(_render_html(report), encoding="utf-8")
    index_path = output_path / "index.html"
    index_path.write_text(_render_report_index_html(report, html_path.name), encoding="utf-8")
    return html_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate an at-a-glance visual overview of one or more FOM modules.")
    parser.add_argument(
        "sources",
        nargs="*",
        help="FOM/MIM module designators to visualize. Defaults to TargetRadarFOMmodule.xml.",
    )
    parser.add_argument(
        "--no-standard-mim",
        action="store_true",
        help="Do not merge the built-in standard MIM into the overview.",
    )
    parser.add_argument(
        "--mim",
        default=None,
        help="Optional explicit MIM designator to merge before the user modules.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for the generated overview artifacts.",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Also write an interactive HTML overview alongside the JSON and Markdown outputs.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional custom report title.",
    )
    args = parser.parse_args(argv)

    sources = args.sources or ("TargetRadarFOMmodule.xml",)
    write_fom_overview(
        sources,
        output_dir=args.output_dir,
        include_standard_mim=not args.no_standard_mim,
        mim_source=args.mim,
        title=args.title,
    )
    if args.html:
        write_fom_overview_html(
            sources,
            output_dir=args.output_dir,
            include_standard_mim=not args.no_standard_mim,
            mim_source=args.mim,
            title=args.title,
        )
    return 0


__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "FOMNodeRow",
    "FOMOverviewReport",
    "build_fom_overview",
    "main",
    "write_fom_overview_html",
    "write_fom_overview",
]
