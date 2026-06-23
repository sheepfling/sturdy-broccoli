"""Corpus classification helpers for the current FOM/XML inventory."""

from __future__ import annotations

import html
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from hla.verification.repo_internal.fom_inventory import FOMInventoryRecord, inventory_records


@dataclass(frozen=True, slots=True)
class FOMCorpusClassificationRow:
    id: str
    path: str
    edition_class: str
    edition_scope: str
    baseline_kind: str
    scenario_family: str
    bucket: str
    rationale: str
    tags: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["tags"] = list(self.tags)
        return payload


@dataclass(frozen=True, slots=True)
class FOMSyntheticNegativeFixture:
    source: str
    purpose: str
    notes: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FOMCorpusClassificationReport:
    title: str
    total_records: int
    bucket_counts: dict[str, int]
    bucket_rows: tuple[FOMCorpusClassificationRow, ...]
    synthetic_negative_fixtures: tuple[FOMSyntheticNegativeFixture, ...]

    def to_json(self) -> str:
        return json.dumps(
            {
                "title": self.title,
                "total_records": self.total_records,
                "bucket_counts": self.bucket_counts,
                "bucket_rows": [row.as_dict() for row in self.bucket_rows],
                "synthetic_negative_fixtures": [fixture.as_dict() for fixture in self.synthetic_negative_fixtures],
            },
            indent=2,
            sort_keys=True,
        )


_SUPPORT_ONLY_FAMILIES = {
    "siso-ieee-1516",
    "siso-omt",
}

_SUPPORT_ONLY_TAGS = {
    "supporting-doc",
}

_SUPPORT_ONLY_NAME_HINTS = (
    ".xsd",
    "schema",
    "readme",
    "guide",
    "manual",
    "doc",
)

_SYNTHETIC_NEGATIVES = (
    FOMSyntheticNegativeFixture(
        source="tests/factories/test_fom_validate.py::test_fom_validate_tool_returns_nonzero_and_writes_issue_report_for_invalid_2025_xml",
        purpose="Negative 2025 validator smoke case for malformed identification content.",
        notes="This fixture is intentionally invalid and belongs in the synthetic-negative lane, not the corpus inventory.",
    ),
    FOMSyntheticNegativeFixture(
        source="tests/test_rti1516_2025_validation.py::test_2025_omt_schema_validation_rejects_enumeration_domains",
        purpose="Negative 2025 OMT schema enumeration-domain coverage.",
        notes="This is a generated schema failure matrix entry, not a cataloged standard module.",
    ),
    FOMSyntheticNegativeFixture(
        source="tests/test_rti1516_2025_validation.py::test_2025_omt_schema_validation_rejects_named_keyref_and_unique_constraints",
        purpose="Negative 2025 OMT schema keyref/unique-constraint coverage.",
        notes="This is a generated schema failure matrix entry, not a cataloged standard module.",
    ),
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


def classify_fom_inventory_record(record: FOMInventoryRecord) -> tuple[str, str]:
    tags = {tag.lower() for tag in record.tags}
    path_name = Path(record.path).name.lower()
    notes = record.notes.lower()

    if record.baseline_kind == "repo-owned":
        return "repo-owned-smoke", "Repo-owned baseline used for smoke, parser, and round-trip coverage."

    if (
        record.scenario_family in _SUPPORT_ONLY_FAMILIES
        or tags & _SUPPORT_ONLY_TAGS
        or any(hint in path_name for hint in _SUPPORT_ONLY_NAME_HINTS)
        or any(hint in notes for hint in _SUPPORT_ONLY_NAME_HINTS)
    ):
        return "support-only", "Schema/support artifact rather than a primary FOM parser input."

    return "authoritative-standard", "Third-party standard or public baseline XML suitable for parser and XML validation coverage."


def classify_edition_scope(record: FOMInventoryRecord) -> str:
    tags = {tag.lower() for tag in getattr(record, "tags", ())}
    baseline_kind = str(getattr(record, "baseline_kind", ""))
    scenario_family = str(getattr(record, "scenario_family", ""))
    edition_class = str(getattr(record, "edition_class", ""))
    path_name = Path(str(getattr(record, "path", ""))).name.lower()

    if baseline_kind == "repo-owned" and scenario_family in _SUPPORT_ONLY_FAMILIES:
        return "schema-only / support-only"
    if tags & _SUPPORT_ONLY_TAGS or any(hint in path_name for hint in _SUPPORT_ONLY_NAME_HINTS):
        return "schema-only / support-only"
    if edition_class == "2010":
        return "2010 only"
    if edition_class == "2025":
        return "2025 only"
    if edition_class == "cross-edition":
        return "both"
    return "cross-edition / ambiguous"


def build_fom_corpus_classification(
    records: Iterable[FOMInventoryRecord] | None = None,
    *,
    title: str = "FOM Corpus Classification",
) -> FOMCorpusClassificationReport:
    rows: list[FOMCorpusClassificationRow] = []
    for record in records if records is not None else inventory_records():
        bucket, rationale = classify_fom_inventory_record(record)
        rows.append(
            FOMCorpusClassificationRow(
                id=record.id,
                path=record.path,
                edition_class=record.edition_class,
                edition_scope=classify_edition_scope(record),
                baseline_kind=record.baseline_kind,
                scenario_family=record.scenario_family,
                bucket=bucket,
                rationale=rationale,
                tags=record.tags,
            )
        )
    rows.sort(key=lambda row: (row.bucket, row.scenario_family, row.path))
    bucket_counts: dict[str, int] = {}
    for row in rows:
        bucket_counts[row.bucket] = bucket_counts.get(row.bucket, 0) + 1
    for bucket in ("authoritative-standard", "repo-owned-smoke", "support-only"):
        bucket_counts.setdefault(bucket, 0)
    return FOMCorpusClassificationReport(
        title=title,
        total_records=len(rows),
        bucket_counts=bucket_counts,
        bucket_rows=tuple(rows),
        synthetic_negative_fixtures=_SYNTHETIC_NEGATIVES,
    )


def render_fom_corpus_classification_markdown(report: FOMCorpusClassificationReport) -> str:
    lines = [
        f"# {report.title}",
        "",
        "Inventory buckets for the repo-owned and third-party XML corpus.",
        "",
        "| Bucket | Count |",
        "| --- | --- |",
    ]
    for bucket in ("authoritative-standard", "repo-owned-smoke", "support-only"):
        lines.append(f"| `{bucket}` | `{report.bucket_counts.get(bucket, 0)}` |")

    for bucket in ("authoritative-standard", "repo-owned-smoke", "support-only"):
        bucket_rows = [row for row in report.bucket_rows if row.bucket == bucket]
        lines.extend(
            [
                "",
                f"## {bucket}",
                "",
                "| ID | Edition | Edition Scope | Baseline | Scenario Family | Tags | Path | Rationale |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        if not bucket_rows:
            lines.append("| _none_ | _n/a_ | _n/a_ | _n/a_ | _n/a_ | _n/a_ | _No rows classified into this bucket._ |")
            continue
        for row in bucket_rows:
            lines.append(
                "| "
                + " | ".join(
                    (
                        f"`{row.id}`",
                        f"`{row.edition_class}`",
                        f"`{row.edition_scope}`",
                        f"`{row.baseline_kind}`",
                        f"`{row.scenario_family}`",
                        ", ".join(f"`{tag}`" for tag in row.tags) if row.tags else "_none_",
                        row.path,
                        row.rationale,
                    )
                )
                + " |"
            )

    lines.extend(
        [
            "",
            "## Synthetic Negatives",
            "",
            "These are intentionally invalid fixtures and are not part of the inventory corpus.",
            "",
            "| Source | Purpose | Notes |",
            "| --- | --- | --- |",
        ]
    )
    for fixture in report.synthetic_negative_fixtures:
        lines.append(f"| `{fixture.source}` | {fixture.purpose} | {fixture.notes} |")

    return "\n".join(lines) + "\n"


def render_fom_corpus_classification_html(report: FOMCorpusClassificationReport) -> str:
    report_json = html.escape(report.to_json())
    bucket_cards = "".join(
        f'<div class="card"><div class="label">{html.escape(bucket)}</div><div class="value">{report.bucket_counts.get(bucket, 0)}</div></div>'
        for bucket in ("authoritative-standard", "repo-owned-smoke", "support-only")
    )
    bucket_sections: list[str] = []
    for bucket in ("authoritative-standard", "repo-owned-smoke", "support-only"):
        bucket_rows = [row for row in report.bucket_rows if row.bucket == bucket]
        rows_html = "".join(
            "<tr>"
            f"<td><code>{html.escape(row.id)}</code></td>"
            f"<td>{html.escape(row.edition_class)}</td>"
            f"<td>{html.escape(row.edition_scope)}</td>"
            f"<td>{html.escape(row.baseline_kind)}</td>"
            f"<td>{html.escape(row.scenario_family)}</td>"
            f"<td>{html.escape(', '.join(row.tags) or 'none')}</td>"
            f"<td><code>{html.escape(row.path)}</code></td>"
            f"<td>{html.escape(row.rationale)}</td>"
            "</tr>"
            for row in bucket_rows
        )
        bucket_sections.append(
            f"""
            <section class="panel">
              <h2>{html.escape(bucket)}</h2>
              <table>
                <thead><tr><th>ID</th><th>Edition</th><th>Edition Scope</th><th>Baseline</th><th>Scenario Family</th><th>Tags</th><th>Path</th><th>Rationale</th></tr></thead>
                <tbody>{rows_html or '<tr><td colspan="8">No rows classified into this bucket.</td></tr>'}</tbody>
              </table>
            </section>
            """
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(report.title)} | FOM Corpus Classification</title>
  <style>
    :root {{ color-scheme: light; --bg: #f5f0e7; --panel: #fffdf8; --ink: #1f2528; --muted: #5e6a71; --line: #d8d0c1; }}
    body {{ margin: 0; font: 15px/1.5 ui-sans-serif, system-ui, sans-serif; color: var(--ink); background: radial-gradient(circle at top, #fff7df, var(--bg) 55%); }}
    main {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 16px; box-shadow: 0 8px 24px rgba(0,0,0,.05); margin-bottom: 16px; }}
    .cards {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); }}
    .card {{ border: 1px solid var(--line); border-radius: 12px; padding: 12px; background: #fff; }}
    .label {{ color: var(--muted); font-size: .9rem; text-transform: uppercase; letter-spacing: .05em; }}
    .value {{ font-size: 1.6rem; font-weight: 700; margin-top: 6px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid var(--line); vertical-align: top; }}
    code {{ background: #f6f3eb; padding: 2px 6px; border-radius: 6px; }}
    .muted {{ color: var(--muted); }}
  </style>
</head>
<body>
<main>
  <section class="panel">
    <h1>{html.escape(report.title)}</h1>
    <p class="muted">Inventory buckets for the repo-owned and third-party XML corpus.</p>
    <div class="cards">{bucket_cards}</div>
    <p class="muted">Total records: {report.total_records}</p>
  </section>
  {''.join(bucket_sections)}
  <section class="panel">
    <h2>Synthetic Negatives</h2>
    <table>
      <thead><tr><th>Source</th><th>Purpose</th><th>Notes</th></tr></thead>
      <tbody>
        {''.join(f'<tr><td><code>{html.escape(fixture.source)}</code></td><td>{html.escape(fixture.purpose)}</td><td>{html.escape(fixture.notes)}</td></tr>' for fixture in report.synthetic_negative_fixtures)}
      </tbody>
    </table>
  </section>
  <script type="application/json" id="payload">{report_json}</script>
</main>
</body>
</html>
"""


def write_fom_corpus_classification(
    output_root: str | Path | None = None,
    *,
    records: Iterable[FOMInventoryRecord] | None = None,
    title: str = "FOM Corpus Classification",
) -> tuple[Path, Path, FOMCorpusClassificationReport]:
    root = Path(output_root) if output_root is not None else _repo_root() / "analysis" / "fom_corpus_classification"
    root.mkdir(parents=True, exist_ok=True)
    report = build_fom_corpus_classification(records, title=title)
    json_path = root / "fom_corpus_classification.json"
    md_path = root / "fom_corpus_classification.md"
    html_path = root / "fom_corpus_classification.html"
    json_path.write_text(report.to_json() + "\n", encoding="utf-8")
    md_path.write_text(render_fom_corpus_classification_markdown(report), encoding="utf-8")
    html_path.write_text(render_fom_corpus_classification_html(report), encoding="utf-8")
    return json_path, md_path, report


__all__ = [
    "FOMCorpusClassificationReport",
    "FOMCorpusClassificationRow",
    "FOMSyntheticNegativeFixture",
    "build_fom_corpus_classification",
    "classify_fom_inventory_record",
    "classify_edition_scope",
    "render_fom_corpus_classification_markdown",
    "render_fom_corpus_classification_html",
    "write_fom_corpus_classification",
]
