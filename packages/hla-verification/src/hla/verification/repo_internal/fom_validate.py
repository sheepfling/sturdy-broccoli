"""User-facing FOM XML validation report helpers."""

from __future__ import annotations

import json
import os
import html
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Literal

from hla.rti1516_2025.validation import ValidationIssue, validate_fom_module, validate_omt_xml_schema
from hla.rti1516e.fom import (
    merge_fom_modules,
    FOMResolver,
    FOMModule,
    FOMResolutionError,
    OMTConformanceAssessment,
    assess_omt_conformance,
    parse_fom_xml,
)
from hla.verification.repo_internal.fom_inventory import default_load_set_for_family, lookup_fom_inventory

Edition = Literal["2010", "2025"]
EditionArg = Literal["auto", "2010", "2025"]
ProfileArg = Literal["auto", "dif", "omt"]

_REPORT_BASENAME = "fom_validation_report"
_ROOT_2025_NAMESPACE = "http://standards.ieee.org/IEEE1516-2025"
_DEFAULT_2025_SCHEMA = Path(
    "docs/requirements/ieee-1516-2025/encoding_auth_work_packet/09-standards-subset/IEEE1516-OMT-2025.xsd"
)


@dataclass(frozen=True, slots=True)
class FOMValidationIssueRow:
    layer: str
    requirement: str | None
    table: str | None
    field: str | None
    value: str | None
    message: str

    def as_dict(self) -> dict[str, str | None]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FOMValidationSourceReport:
    source: str
    effective_edition: Edition
    inventory_id: str | None
    inventory_edition_class: str | None
    baseline_kind: str | None
    load_mode: str | None
    scenario_family: str | None
    profile: str
    schema_path: str | None
    verdict: str
    passed: bool
    schema_valid: bool
    parsed: bool
    semantic_valid: bool
    module_name: str | None
    object_classes: int
    interaction_classes: int
    datatype_names: int
    dimensions: tuple[str, ...]
    rationale: str
    recommended_next_step: str
    unsupported_features: tuple[str, ...]
    issues: tuple[FOMValidationIssueRow, ...]

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["dimensions"] = list(self.dimensions)
        payload["unsupported_features"] = list(self.unsupported_features)
        payload["issues"] = [issue.as_dict() for issue in self.issues]
        return payload


@dataclass(frozen=True, slots=True)
class FOMValidationLoadSetReport:
    name: str
    kind: str
    source_paths: tuple[str, ...]
    effective_edition: Edition
    inventory_edition_classes: tuple[str, ...]
    baseline_kinds: tuple[str, ...]
    load_mode: str
    profile: str
    schema_path: str | None
    verdict: str
    passed: bool
    parsed: bool
    semantic_valid: bool
    module_names: tuple[str, ...]
    member_summaries: tuple[dict[str, Any], ...]
    object_classes: int
    interaction_classes: int
    datatype_names: int
    dimensions: tuple[str, ...]
    rationale: str
    recommended_next_step: str
    issues: tuple[FOMValidationIssueRow, ...]

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["issues"] = [issue.as_dict() for issue in self.issues]
        return payload


@dataclass(frozen=True, slots=True)
class FOMValidationReport:
    title: str
    sources: tuple[str, ...]
    families: tuple[str, ...]
    edition_request: EditionArg
    profile_request: ProfileArg
    strict_identification: bool
    schema_path: str | None
    source_reports: tuple[FOMValidationSourceReport, ...]
    load_set_reports: tuple[FOMValidationLoadSetReport, ...]

    def to_json(self) -> str:
        return json.dumps(
            {
                "title": self.title,
                "sources": list(self.sources),
                "families": list(self.families),
                "edition_request": self.edition_request,
                "profile_request": self.profile_request,
                "strict_identification": self.strict_identification,
                "schema_path": self.schema_path,
                "source_reports": [row.as_dict() for row in self.source_reports],
                "load_set_reports": [row.as_dict() for row in self.load_set_reports],
            },
            indent=2,
            sort_keys=True,
        )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


def _sniff_effective_edition(source: Path) -> Edition:
    try:
        root = ET.parse(source).getroot()
    except ET.ParseError:
        text = source.read_text(encoding="utf-8", errors="ignore")[:4096]
        return "2025" if _ROOT_2025_NAMESPACE in text else "2010"
    return "2025" if root.tag.startswith(f"{{{_ROOT_2025_NAMESPACE}}}") else "2010"


def _normalize_edition(source: Path, requested: EditionArg) -> Edition:
    if requested != "auto":
        return requested
    inventory = lookup_fom_inventory(source)
    if inventory is not None and inventory.edition_class in {"2010", "2025"}:
        return inventory.edition_class
    if not source.exists():
        try:
            resolved = FOMResolver().resolve(str(source))
        except Exception:
            return "2010"
        resolved_path = Path(str(resolved.path or resolved.source))
        if resolved_path.exists():
            return _sniff_effective_edition(resolved_path)
    return _sniff_effective_edition(source)


def _normalize_profile(effective_edition: Edition, requested: ProfileArg) -> str:
    if effective_edition == "2025":
        return "omt-2025"
    if requested == "auto":
        return "dif"
    return requested


def _resolve_source_path(source: str | Path, *, effective_edition: Edition) -> Path:
    candidate = Path(source)
    if candidate.exists():
        return candidate
    resolver = FOMResolver()
    resolved = resolver.resolve(str(source))
    resolved_path = Path(str(resolved.path or resolved.source))
    if resolved_path.exists():
        return resolved_path
    raise FileNotFoundError(f"Could not resolve XML source {source!r} on the {effective_edition} validator path")


def _module_counts(module: FOMModule | None) -> tuple[int, int, int, tuple[str, ...]]:
    if module is None:
        return 0, 0, 0, ()
    return (
        len(module.object_classes),
        len(module.interaction_classes),
        len(module.datatype_names),
        tuple(module.dimensions),
    )


def _member_summary(module: FOMModule) -> dict[str, Any]:
    return {
        "source": str(module.source),
        "name": module.name,
        "object_classes": tuple(sorted(spec.full_name for spec in module.object_classes)),
        "interaction_classes": tuple(sorted(spec.full_name for spec in module.interaction_classes)),
        "datatype_names": tuple(sorted(module.datatype_names)),
        "dimensions": tuple(module.dimensions),
    }


def _recommendation(verdict: str, issues: tuple[FOMValidationIssueRow, ...], unsupported: tuple[str, ...]) -> str:
    if verdict == "conforming":
        return "Safe to use this XML on the current validator path."
    if verdict == "partially-conforming":
        if unsupported:
            return "Schema and parser checks pass; review the unsupported subset notes before relying on runtime behavior."
        return "Review the reported subset caveats before treating this module as fully supported."
    if verdict == "parse-failed":
        return "Fix the malformed or unsupported XML structure first; schema and semantic diagnostics may be secondary."
    if any(issue.layer == "schema" for issue in issues):
        return "Fix the XML/XSD errors first, then rerun semantic validation."
    if any(issue.layer == "semantic" for issue in issues):
        return "Fix the semantic validator findings, then rerun the full validation path."
    return "Review the reported validation issues and rerun the validator after correction."


def _load_set_recommendation(verdict: str, issues: tuple[FOMValidationIssueRow, ...]) -> str:
    if verdict == "conforming":
        return "The merged load set is valid on the current validator path."
    if verdict == "parse-failed":
        return "Fix the member XMLs or their merge order before trusting this load set."
    if any(issue.layer == "merge" for issue in issues):
        return "Fix the merge conflict or member ordering, then rerun the load-set validation."
    if any(issue.layer == "semantic" for issue in issues):
        return "Fix the merged semantic validation findings, then rerun the load-set validation."
    return "Review the merged load-set issues and rerun validation."


class _working_directory:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._previous: str | None = None

    def __enter__(self) -> None:
        self._previous = os.getcwd()
        os.chdir(self._path)

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self._previous is not None:
            os.chdir(self._previous)


def _markdown(report: FOMValidationReport) -> str:
    lines = [
        f"# {report.title}",
        "",
        f"- Edition request: `{report.edition_request}`",
        f"- Profile request: `{report.profile_request}`",
        f"- Strict identification: `{str(report.strict_identification).lower()}`",
    ]
    if report.schema_path is not None:
        lines.append(f"- Schema path: `{report.schema_path}`")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            "| Source | Effective Edition | Catalog Class | Verdict | Passed | Schema | Parsed | Semantic | Scenario Family |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.source_reports:
        lines.append(
            "| "
            + " | ".join(
                (
                    f"`{row.source}`",
                    row.effective_edition,
                    row.inventory_edition_class or "unclassified",
                    row.verdict,
                    "yes" if row.passed else "no",
                    "yes" if row.schema_valid else "no",
                    "yes" if row.parsed else "no",
                    "yes" if row.semantic_valid else "no",
                    row.scenario_family or "n/a",
                )
            )
            + " |"
        )
    if report.load_set_reports:
        lines.extend(
            [
                "",
                "## Load Sets",
                "",
                "| Load Set | Kind | Effective Edition | Verdict | Passed | Parsed | Semantic | Members |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in report.load_set_reports:
            lines.append(
                "| "
                + " | ".join(
                    (
                        f"`{row.name}`",
                        row.kind,
                        row.effective_edition,
                        row.verdict,
                        "yes" if row.passed else "no",
                        "yes" if row.parsed else "no",
                        "yes" if row.semantic_valid else "no",
                        str(len(row.source_paths)),
                    )
                )
                + " |"
            )
    for row in report.source_reports:
        lines.extend(
            [
                "",
                f"## `{row.source}`",
                "",
                f"- Effective edition: `{row.effective_edition}`",
                f"- Catalog class: `{row.inventory_edition_class or 'unclassified'}`",
                f"- Baseline kind: `{row.baseline_kind or 'n/a'}`",
                f"- Load mode: `{row.load_mode or 'n/a'}`",
                f"- Scenario family: `{row.scenario_family or 'n/a'}`",
                f"- Profile: `{row.profile}`",
                f"- Verdict: `{row.verdict}`",
                f"- Recommended next step: {row.recommended_next_step}",
                f"- Rationale: {row.rationale}",
                "",
                "### Structure",
                "",
                f"- Module name: `{row.module_name or 'n/a'}`",
                f"- Object classes: `{row.object_classes}`",
                f"- Interaction classes: `{row.interaction_classes}`",
                f"- Datatype names: `{row.datatype_names}`",
                f"- Dimensions: `{', '.join(row.dimensions) if row.dimensions else 'none'}`",
            ]
        )
        if row.unsupported_features:
            lines.extend(["", "### Unsupported / Narrowed Subset Notes", ""])
            for item in row.unsupported_features:
                lines.append(f"- {item}")
        if row.issues:
            lines.extend(
                [
                    "",
                    "### Issues",
                    "",
                    "| Layer | Requirement | Field | Message |",
                    "| --- | --- | --- | --- |",
                ]
            )
            for issue in row.issues:
                lines.append(
                    "| "
                    + " | ".join(
                        (
                            issue.layer,
                            issue.requirement or "n/a",
                            issue.field or "n/a",
                            issue.message.replace("\n", " "),
                        )
                    )
                    + " |"
                )
        else:
            lines.extend(["", "### Issues", "", "- none"])
    for row in report.load_set_reports:
        lines.extend(
            [
                "",
                f"## Load Set `{row.name}`",
                "",
                f"- Kind: `{row.kind}`",
                f"- Effective edition: `{row.effective_edition}`",
                f"- Load mode: `{row.load_mode}`",
                f"- Catalog classes: `{', '.join(row.inventory_edition_classes)}`",
                f"- Baseline kinds: `{', '.join(row.baseline_kinds)}`",
                f"- Profile: `{row.profile}`",
                f"- Verdict: `{row.verdict}`",
                f"- Recommended next step: {row.recommended_next_step}",
                f"- Rationale: {row.rationale}",
                "",
                "### Members",
                "",
            ]
        )
        for path in row.source_paths:
            lines.append(f"- `{path}`")
        lines.extend(
            [
                "",
                "### Structure",
                "",
                f"- Module names: `{', '.join(row.module_names) if row.module_names else 'n/a'}`",
                f"- Object classes: `{row.object_classes}`",
                f"- Interaction classes: `{row.interaction_classes}`",
                f"- Datatype names: `{row.datatype_names}`",
                f"- Dimensions: `{', '.join(row.dimensions) if row.dimensions else 'none'}`",
            ]
        )
        if row.issues:
            lines.extend(
                [
                    "",
                    "### Issues",
                    "",
                    "| Layer | Requirement | Field | Message |",
                    "| --- | --- | --- | --- |",
                ]
            )
            for issue in row.issues:
                lines.append(
                    "| "
                    + " | ".join(
                        (
                            issue.layer,
                            issue.requirement or "n/a",
                            issue.field or "n/a",
                            issue.message.replace("\n", " "),
                        )
                    )
                    + " |"
                )
        else:
            lines.extend(["", "### Issues", "", "- none"])
    return "\n".join(lines) + "\n"


def _html_report(report: FOMValidationReport) -> str:
    report_json = report.to_json()
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(report.title)} | FOM Validate</title>
  <style>
    :root {{ color-scheme: light; --bg: #f4f1e8; --panel: #fffdf8; --ink: #1f2528; --muted: #59656d; --line: #d8d0c1; --good: #2e6b4f; --bad: #8a2f2f; --warn: #8a6a1f; }}
    body {{ margin: 0; font: 15px/1.5 ui-sans-serif, system-ui, sans-serif; color: var(--ink); background: radial-gradient(circle at top, #fff7dd, var(--bg) 55%); }}
    main {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
    h1,h2,h3 {{ margin: 0 0 12px; }}
    .grid {{ display: grid; gap: 16px; grid-template-columns: 320px 1fr; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 16px; box-shadow: 0 8px 24px rgba(0,0,0,.05); }}
    .cards {{ display: grid; gap: 12px; }}
    .card {{ border: 1px solid var(--line); border-radius: 12px; padding: 12px; cursor: pointer; background: #fff; }}
    .card.active {{ outline: 2px solid #b77b2a; }}
    .muted {{ color: var(--muted); }}
    .status-good {{ color: var(--good); font-weight: 700; }}
    .status-bad {{ color: var(--bad); font-weight: 700; }}
    .status-warn {{ color: var(--warn); font-weight: 700; }}
    code {{ background: #f6f3eb; padding: 2px 6px; border-radius: 6px; }}
    ul {{ padding-left: 18px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid var(--line); vertical-align: top; }}
    .toolbar {{ display: flex; gap: 8px; margin: 0 0 16px; }}
    input, select {{ width: 100%; padding: 10px 12px; border: 1px solid var(--line); border-radius: 10px; background: #fff; }}
    .split {{ display: grid; gap: 12px; grid-template-columns: 1fr 1fr; margin: 12px 0; }}
    @media (max-width: 900px) {{ .grid, .split {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
<main>
  <div class="panel" style="margin-bottom:16px;">
    <h1>{html.escape(report.title)}</h1>
    <p class="muted">Single-command XML validation with source-level and load-set-level results.</p>
    <div class="toolbar">
      <input id="filterBox" type="search" placeholder="Filter by path, family, verdict, or edition">
      <select id="viewMode">
        <option value="source">Source reports</option>
        <option value="loadset">Load-set reports</option>
      </select>
    </div>
  </div>
  <div class="grid">
    <section class="panel">
      <div id="listHost" class="cards"></div>
    </section>
    <section class="panel">
      <div id="detailHost"></div>
    </section>
  </div>
</main>
<script type="application/json" id="payload">{html.escape(report_json)}</script>
<script>
const payload = JSON.parse(document.getElementById("payload").textContent);
const listHost = document.getElementById("listHost");
const detailHost = document.getElementById("detailHost");
const filterBox = document.getElementById("filterBox");
const viewMode = document.getElementById("viewMode");
let activeIndex = 0;
function items() {{
  return viewMode.value === "loadset" ? payload.load_set_reports : payload.source_reports;
}}
function badgeClass(verdict) {{
  if (verdict === "conforming") return "status-good";
  if (verdict === "partially-conforming") return "status-warn";
  return "status-bad";
}}
function haystack(item) {{
  return JSON.stringify(item).toLowerCase();
}}
function renderList() {{
  const rows = items();
  const filtered = rows.map((row, index) => [row, index]).filter(([row]) => haystack(row).includes(filterBox.value.toLowerCase()));
  if (!filtered.length) {{
    listHost.innerHTML = '<p class="muted">No matches.</p>';
    detailHost.innerHTML = '<p class="muted">No detail to show.</p>';
    return;
  }}
  if (!filtered.some(([, index]) => index === activeIndex)) activeIndex = filtered[0][1];
  listHost.innerHTML = filtered.map(([row, index]) => {{
    const title = viewMode.value === "loadset" ? row.name : row.source;
    const subtitle = viewMode.value === "loadset" ? `${{row.kind}} | ${{row.effective_edition}}` : `${{row.scenario_family || "n/a"}} | ${{row.effective_edition}}`;
    return `<div class="card ${{index === activeIndex ? "active" : ""}}" data-index="${{index}}">
      <div><strong>${{title}}</strong></div>
      <div class="muted">${{subtitle}}</div>
      <div class="${{badgeClass(row.verdict)}}">${{row.verdict}}</div>
    </div>`;
  }}).join("");
  Array.from(listHost.querySelectorAll(".card")).forEach((node) => node.addEventListener("click", () => {{
    activeIndex = Number(node.dataset.index);
    renderList();
    renderDetail();
  }}));
  renderDetail();
}}
function issueTable(issues) {{
  if (!issues.length) return '<p class="muted">No issues.</p>';
  return `<table><thead><tr><th>Layer</th><th>Requirement</th><th>Field</th><th>Message</th></tr></thead><tbody>${{issues.map((issue) => `<tr><td>${{issue.layer}}</td><td>${{issue.requirement || "n/a"}}</td><td>${{issue.field || "n/a"}}</td><td>${{issue.message}}</td></tr>`).join("")}}</tbody></table>`;
}}
function diffLists(left, right) {{
  const leftSet = new Set(left);
  const rightSet = new Set(right);
  return {{
    shared: [...leftSet].filter((item) => rightSet.has(item)).sort(),
    onlyLeft: [...leftSet].filter((item) => !rightSet.has(item)).sort(),
    onlyRight: [...rightSet].filter((item) => !leftSet.has(item)).sort(),
  }};
}}
function listBlock(items) {{
  if (!items.length) return '<p class="muted">none</p>';
  return `<div class="list">${{items.map((item) => `<code>${{item}}</code>`).join("")}}</div>`;
}}
function loadSetDiffWidget(row) {{
  if (!row.member_summaries || row.member_summaries.length < 2) return "";
  return `
    <h3>Side-by-Side Member Tree Diff</h3>
    <div class="toolbar">
      <select id="loadset-left"></select>
      <select id="loadset-right"></select>
    </div>
    <div id="loadset-diff"></div>
  `;
}}
function renderLoadSetDiff(row) {{
  const leftSel = document.getElementById("loadset-left");
  const rightSel = document.getElementById("loadset-right");
  const host = document.getElementById("loadset-diff");
  if (!leftSel || !rightSel || !host) return;
  const options = row.member_summaries.map((member, index) => `<option value="${{index}}">${{member.name || member.source}}</option>`).join("");
  if (!leftSel.dataset.ready) {{
    leftSel.innerHTML = options;
    rightSel.innerHTML = options;
    leftSel.value = "0";
    rightSel.value = String(Math.min(1, row.member_summaries.length - 1));
    leftSel.dataset.ready = "1";
    rightSel.dataset.ready = "1";
    leftSel.onchange = () => renderLoadSetDiff(row);
    rightSel.onchange = () => renderLoadSetDiff(row);
  }}
  if (leftSel.value === rightSel.value) {{
    host.innerHTML = '<p class="muted">Select two distinct members.</p>';
    return;
  }}
  const left = row.member_summaries[Number(leftSel.value)];
  const right = row.member_summaries[Number(rightSel.value)];
  const objectDiff = diffLists(left.object_classes, right.object_classes);
  const interactionDiff = diffLists(left.interaction_classes, right.interaction_classes);
  host.innerHTML = `
    <p><strong>${{left.name || left.source}}</strong> vs <strong>${{right.name || right.source}}</strong></p>
    <div class="split">
      <div>
        <h4>Only Left Objects</h4>
        ${{listBlock(objectDiff.onlyLeft)}}
      </div>
      <div>
        <h4>Only Right Objects</h4>
        ${{listBlock(objectDiff.onlyRight)}}
      </div>
    </div>
    <div class="split">
      <div>
        <h4>Only Left Interactions</h4>
        ${{listBlock(interactionDiff.onlyLeft)}}
      </div>
      <div>
        <h4>Only Right Interactions</h4>
        ${{listBlock(interactionDiff.onlyRight)}}
      </div>
    </div>
    <div class="split">
      <div>
        <h4>Shared Objects</h4>
        ${{listBlock(objectDiff.shared.slice(0, 120))}}
      </div>
      <div>
        <h4>Shared Interactions</h4>
        ${{listBlock(interactionDiff.shared.slice(0, 120))}}
      </div>
    </div>
  `;
}}
function renderDetail() {{
  const row = items()[activeIndex];
  if (!row) {{
    detailHost.innerHTML = '<p class="muted">Select a report.</p>';
    return;
  }}
  if (viewMode.value === "loadset") {{
    detailHost.innerHTML = `
      <h2>${{row.name}}</h2>
      <p class="${{badgeClass(row.verdict)}}">${{row.verdict}}</p>
      <p>${{row.rationale}}</p>
      <p><strong>Next step:</strong> ${{row.recommended_next_step}}</p>
      <p><strong>Members:</strong></p>
      <ul>${{row.source_paths.map((path) => `<li><code>${{path}}</code></li>`).join("")}}</ul>
      <p><strong>Counts:</strong> objects=${{row.object_classes}}, interactions=${{row.interaction_classes}}, datatypes=${{row.datatype_names}}</p>
      <p><strong>Dimensions:</strong> ${{row.dimensions.length ? row.dimensions.join(", ") : "none"}}</p>
      ${{loadSetDiffWidget(row)}}
      <h3>Issues</h3>
      ${{issueTable(row.issues)}}
    `;
    renderLoadSetDiff(row);
    return;
  }}
  detailHost.innerHTML = `
    <h2><code>${{row.source}}</code></h2>
    <p class="${{badgeClass(row.verdict)}}">${{row.verdict}}</p>
    <p>${{row.rationale}}</p>
    <p><strong>Next step:</strong> ${{row.recommended_next_step}}</p>
    <ul>
      <li><strong>Effective edition:</strong> ${{row.effective_edition}}</li>
      <li><strong>Catalog class:</strong> ${{row.inventory_edition_class || "unclassified"}}</li>
      <li><strong>Scenario family:</strong> ${{row.scenario_family || "n/a"}}</li>
      <li><strong>Profile:</strong> ${{row.profile}}</li>
      <li><strong>Schema:</strong> ${{row.schema_valid ? "ok" : "fail"}}</li>
      <li><strong>Parsed:</strong> ${{row.parsed ? "ok" : "fail"}}</li>
      <li><strong>Semantic:</strong> ${{row.semantic_valid ? "ok" : "fail"}}</li>
    </ul>
    <p><strong>Counts:</strong> objects=${{row.object_classes}}, interactions=${{row.interaction_classes}}, datatypes=${{row.datatype_names}}</p>
    <p><strong>Dimensions:</strong> ${{row.dimensions.length ? row.dimensions.join(", ") : "none"}}</p>
    <h3>Issues</h3>
    ${{issueTable(row.issues)}}
  `;
}}
filterBox.addEventListener("input", renderList);
viewMode.addEventListener("change", () => {{ activeIndex = 0; renderList(); }});
renderList();
</script>
</body>
</html>
"""


def _assess_2010(source: Path, profile: str) -> FOMValidationSourceReport:
    inventory = lookup_fom_inventory(source, year=2010)
    module: FOMModule | None = None
    issues: list[FOMValidationIssueRow] = []
    assessment: OMTConformanceAssessment | None = None
    parsed = False
    try:
        with _working_directory(_repo_root()):
            assessment = assess_omt_conformance(source, validate_schema=True, profile=profile)
            parsed = assessment.parsed
            if parsed:
                module = parse_fom_xml(source, validate_schema=False)
    except FOMResolutionError as exc:
        issues.append(
            FOMValidationIssueRow(
                layer="parser",
                requirement=None,
                table=None,
                field=None,
                value=None,
                message=str(exc),
            )
        )
    if assessment is None:
        assessment = OMTConformanceAssessment(
            label="nonconforming",
            schema_valid=False,
            parsed=False,
            rationale="The document could not be classified on the 2010 validator path.",
        )
    if assessment.label == "nonconforming" and not issues and assessment.rationale:
        issues.append(
            FOMValidationIssueRow(
                layer="semantic",
                requirement=None,
                table=None,
                field=None,
                value=None,
                message=assessment.rationale,
            )
        )
    object_count, interaction_count, datatype_count, dimensions = _module_counts(module)
    unsupported = tuple(assessment.unsupported_features)
    verdict = assessment.label
    passed = verdict in {"conforming", "partially conforming"}
    normalized_verdict = verdict.replace(" ", "-")
    return FOMValidationSourceReport(
        source=str(source),
        effective_edition="2010",
        inventory_id=inventory.id if inventory is not None else None,
        inventory_edition_class=inventory.edition_class if inventory is not None else None,
        baseline_kind=inventory.baseline_kind if inventory is not None else None,
        load_mode=inventory.load_mode if inventory is not None else None,
        scenario_family=inventory.scenario_family if inventory is not None else None,
        profile=profile,
        schema_path="CERTI/xml/ieee1516-2010/1516_2-2010",
        verdict=normalized_verdict,
        passed=passed,
        schema_valid=assessment.schema_valid,
        parsed=assessment.parsed,
        semantic_valid=assessment.label != "nonconforming",
        module_name=assessment.module_name if module is None else module.name,
        object_classes=object_count,
        interaction_classes=interaction_count,
        datatype_names=datatype_count,
        dimensions=dimensions,
        rationale=assessment.rationale,
        recommended_next_step=_recommendation(normalized_verdict, tuple(issues), unsupported),
        unsupported_features=unsupported,
        issues=tuple(issues),
    )


def _assess_2025(source: Path, schema_path: Path, strict_identification: bool) -> FOMValidationSourceReport:
    inventory = lookup_fom_inventory(source, year=2025)
    issues: list[FOMValidationIssueRow] = []
    schema_issues = validate_omt_xml_schema(source, schema_path)
    issues.extend(
        FOMValidationIssueRow(
            layer="schema",
            requirement=item.requirement,
            table=item.table,
            field=item.field,
            value=item.value,
            message=item.message,
        )
        for item in schema_issues
    )
    module: FOMModule | None = None
    parse_error: str | None = None
    try:
        module = parse_fom_xml(source, validate_schema=False)
    except FOMResolutionError as exc:
        parse_error = str(exc)
        issues.append(
            FOMValidationIssueRow(
                layer="parser",
                requirement=None,
                table=None,
                field=None,
                value=None,
                message=parse_error,
            )
        )
    semantic_issues: list[ValidationIssue] = []
    if module is not None:
        semantic_issues = validate_fom_module(module, strict_identification=strict_identification)
        issues.extend(
            FOMValidationIssueRow(
                layer="semantic",
                requirement=item.requirement,
                table=item.table,
                field=item.field,
                value=item.value,
                message=item.message,
            )
            for item in semantic_issues
        )
    object_count, interaction_count, datatype_count, dimensions = _module_counts(module)
    if parse_error is not None:
        verdict = "parse-failed"
        rationale = "The XML could not be parsed into the repo-native FOM model."
        passed = False
        semantic_valid = False
    elif schema_issues or semantic_issues:
        verdict = "nonconforming"
        rationale = "The XML parsed, but it failed schema validation and/or the 2025 semantic validator."
        passed = False
        semantic_valid = not semantic_issues
    else:
        verdict = "conforming"
        rationale = "The XML passes the current 2025 schema and semantic validation path."
        passed = True
        semantic_valid = True
    return FOMValidationSourceReport(
        source=str(source),
        effective_edition="2025",
        inventory_id=inventory.id if inventory is not None else None,
        inventory_edition_class=inventory.edition_class if inventory is not None else None,
        baseline_kind=inventory.baseline_kind if inventory is not None else None,
        load_mode=inventory.load_mode if inventory is not None else None,
        scenario_family=inventory.scenario_family if inventory is not None else None,
        profile="omt-2025",
        schema_path=str(schema_path),
        verdict=verdict,
        passed=passed,
        schema_valid=not schema_issues,
        parsed=module is not None,
        semantic_valid=semantic_valid,
        module_name=module.name if module is not None else None,
        object_classes=object_count,
        interaction_classes=interaction_count,
        datatype_names=datatype_count,
        dimensions=dimensions,
        rationale=rationale,
        recommended_next_step=_recommendation(verdict, tuple(issues), ()),
        unsupported_features=(),
        issues=tuple(issues),
    )


def _resolve_many_sources(sources: Iterable[str | Path], *, edition: EditionArg) -> tuple[tuple[Path, ...], Edition]:
    raw_sources = tuple(sources)
    if not raw_sources:
        return (), "2010"
    requested = _normalize_edition(Path(raw_sources[0]), edition)
    resolved = tuple(_resolve_source_path(source, effective_edition=requested) for source in raw_sources)
    effective = _normalize_edition(resolved[0], requested)
    return resolved, effective


def _load_set_report(
    name: str,
    kind: str,
    sources: tuple[Path, ...],
    *,
    effective_edition: Edition,
    profile: str,
    strict_identification: bool,
    schema_path: Path,
) -> FOMValidationLoadSetReport:
    resolver = FOMResolver()
    inventories = tuple(lookup_fom_inventory(path, year=effective_edition == "2025" and 2025 or 2010) for path in sources)
    issues: list[FOMValidationIssueRow] = []
    parsed = False
    semantic_valid = False
    verdict = "parse-failed"
    rationale = "The load set could not be merged into a repo-native catalog."
    module_names: tuple[str, ...] = ()
    member_summaries: tuple[dict[str, Any], ...] = ()
    object_classes = 0
    interaction_classes = 0
    datatype_names = 0
    dimensions: tuple[str, ...] = ()
    try:
        resolved_modules = resolver.resolve_many(sources)
        module_names = tuple(module.name or str(module.source) for module in resolved_modules)
        member_summaries = tuple(_member_summary(module) for module in resolved_modules)
        if effective_edition == "2010":
            with _working_directory(_repo_root()):
                merge_fom_modules(resolved_modules)
            parsed = True
            semantic_valid = True
            verdict = "conforming"
            rationale = "The ordered load set merged successfully on the 2010 validator path."
        else:
            merge_fom_modules(resolved_modules)
            parsed = True
            semantic_rows: list[ValidationIssue] = []
            for source in sources:
                semantic_rows.extend(validate_omt_xml_schema(source, schema_path))
            for module in resolved_modules:
                semantic_rows.extend(validate_fom_module(module, strict_identification=strict_identification))
            issues.extend(
                FOMValidationIssueRow(
                    layer="semantic" if item.table != "omtXmlSchema" else "schema",
                    requirement=item.requirement,
                    table=item.table,
                    field=item.field,
                    value=item.value,
                    message=item.message,
                )
                for item in semantic_rows
            )
            semantic_valid = not issues
            verdict = "conforming" if semantic_valid else "nonconforming"
            rationale = (
                "The load set merged and passed schema + semantic validation on the 2025 path."
                if semantic_valid
                else "The load set merged, but one or more member modules failed schema or semantic validation."
            )
        merged_catalog = merge_fom_modules(resolved_modules)
        object_classes = len(merged_catalog.object_classes)
        interaction_classes = len(merged_catalog.interaction_classes)
        datatype_names = len(merged_catalog.datatype_names)
        dimensions = tuple(merged_catalog.dimensions)
    except FOMResolutionError as exc:
        issues.append(
            FOMValidationIssueRow(
                layer="merge",
                requirement=None,
                table=None,
                field=None,
                value=None,
                message=str(exc),
            )
        )
    return FOMValidationLoadSetReport(
        name=name,
        kind=kind,
        source_paths=tuple(str(path) for path in sources),
        effective_edition=effective_edition,
        inventory_edition_classes=tuple(dict.fromkeys(item.edition_class for item in inventories if item is not None)),
        baseline_kinds=tuple(dict.fromkeys(item.baseline_kind for item in inventories if item is not None)),
        load_mode=inventories[0].load_mode if inventories and inventories[0] is not None else "standalone",
        profile=profile,
        schema_path=str(schema_path) if effective_edition == "2025" else "CERTI/xml/ieee1516-2010/1516_2-2010",
        verdict=verdict,
        passed=verdict == "conforming",
        parsed=parsed,
        semantic_valid=semantic_valid,
        module_names=module_names,
        member_summaries=member_summaries,
        object_classes=object_classes,
        interaction_classes=interaction_classes,
        datatype_names=datatype_names,
        dimensions=dimensions,
        rationale=rationale,
        recommended_next_step=_load_set_recommendation(verdict, tuple(issues)),
        issues=tuple(issues),
    )


def build_fom_validation(
    sources: Iterable[str | Path],
    *,
    families: Iterable[str] = (),
    edition: EditionArg = "auto",
    profile: ProfileArg = "auto",
    strict_identification: bool = False,
    schema_path: str | Path | None = None,
    title: str | None = None,
) -> FOMValidationReport:
    raw_sources = tuple(sources)
    normalized_families = tuple(families)
    if not raw_sources and not normalized_families:
        raise ValueError("At least one XML source or one family is required")
    resolved_schema = Path(schema_path) if schema_path is not None else (_repo_root() / _DEFAULT_2025_SCHEMA)
    rows: list[FOMValidationSourceReport] = []
    load_set_rows: list[FOMValidationLoadSetReport] = []
    normalized_sources: list[Path] = []
    for source in raw_sources:
        source_path = Path(source)
        effective = _normalize_edition(source_path, edition)
        resolved_source = _resolve_source_path(source, effective_edition=effective)
        normalized_sources.append(resolved_source)
        if effective == "2010":
            rows.append(_assess_2010(resolved_source, _normalize_profile(effective, profile)))
        else:
            rows.append(_assess_2025(resolved_source, resolved_schema, strict_identification))
    if len(normalized_sources) > 1:
        explicit_effective = _normalize_edition(normalized_sources[0], edition)
        load_set_rows.append(
            _load_set_report(
                "explicit-load-set",
                "explicit",
                tuple(normalized_sources),
                effective_edition=explicit_effective,
                profile=_normalize_profile(explicit_effective, profile),
                strict_identification=strict_identification,
                schema_path=resolved_schema,
            )
        )
    for family in normalized_families:
        family_records = default_load_set_for_family(family)
        family_sources = tuple(_repo_root() / record.path for record in family_records)
        effective = _normalize_edition(family_sources[0], edition)
        load_set_rows.append(
            _load_set_report(
                family,
                "family",
                family_sources,
                effective_edition=effective,
                profile=_normalize_profile(effective, profile),
                strict_identification=strict_identification,
                schema_path=resolved_schema,
            )
        )
    return FOMValidationReport(
        title=title or "FOM Validation Report",
        sources=tuple(str(path) for path in normalized_sources),
        families=normalized_families,
        edition_request=edition,
        profile_request=profile,
        strict_identification=strict_identification,
        schema_path=str(resolved_schema)
        if any(row.effective_edition == "2025" for row in rows) or any(row.effective_edition == "2025" for row in load_set_rows)
        else None,
        source_reports=tuple(rows),
        load_set_reports=tuple(load_set_rows),
    )


def write_fom_validation(
    sources: Iterable[str | Path],
    *,
    output_dir: str | Path,
    families: Iterable[str] = (),
    edition: EditionArg = "auto",
    profile: ProfileArg = "auto",
    strict_identification: bool = False,
    schema_path: str | Path | None = None,
    title: str | None = None,
) -> tuple[Path, Path, FOMValidationReport]:
    report = build_fom_validation(
        sources,
        families=families,
        edition=edition,
        profile=profile,
        strict_identification=strict_identification,
        schema_path=schema_path,
        title=title,
    )
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / f"{_REPORT_BASENAME}.json"
    md_path = output_path / f"{_REPORT_BASENAME}.md"
    json_path.write_text(report.to_json(), encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")
    return json_path, md_path, report


def write_fom_validation_html(
    sources: Iterable[str | Path],
    *,
    output_dir: str | Path,
    families: Iterable[str] = (),
    edition: EditionArg = "auto",
    profile: ProfileArg = "auto",
    strict_identification: bool = False,
    schema_path: str | Path | None = None,
    title: str | None = None,
) -> Path:
    _, _, report = write_fom_validation(
        sources,
        output_dir=output_dir,
        families=families,
        edition=edition,
        profile=profile,
        strict_identification=strict_identification,
        schema_path=schema_path,
        title=title,
    )
    html_path = Path(output_dir) / f"{_REPORT_BASENAME}.html"
    html_path.write_text(_html_report(report), encoding="utf-8")
    return html_path


__all__ = [
    "FOMValidationIssueRow",
    "FOMValidationLoadSetReport",
    "FOMValidationReport",
    "FOMValidationSourceReport",
    "build_fom_validation",
    "write_fom_validation",
    "write_fom_validation_html",
]
