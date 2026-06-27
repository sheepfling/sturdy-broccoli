"""FastAPI federation visualizer service over the shared runtime observer core."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Mapping

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from hla.verification.repo_internal.fom_workbench import write_fom_workbench_html

from .runtime_observer_core import (
    RUNTIME_OBSERVER_EVENT_SCHEMA_VERSION,
    RuntimeObserverControl,
    build_runtime_observer_catalog,
    build_runtime_observer_event_schema,
)


class ObserverStartRequest(BaseModel):
    provider: str
    scenario: str
    backend: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    service: str
    status: str
    schema_version: str
    session_active: bool


class ObserverStopResponse(BaseModel):
    status: str


class NormalizedEventRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    sequence: int
    event_type: str
    provider: str | None = None
    scenario: str | None = None
    family: str | None = None
    source: str | None = None
    observer_role: str | None = None
    phase: str | None = None
    operation: str | None = None
    actor: str | None = None
    target: str | None = None
    details: dict[str, Any] | None = None
    object_key: str | None = None
    object_name: str | None = None
    object_handle_text: str | None = None
    class_name: str | None = None
    class_handle_text: str | None = None
    attributes: dict[str, Any] | None = None
    interaction_key: str | None = None
    interaction_class: str | None = None
    parameters: dict[str, Any] | None = None
    tag: Any | None = None
    payload: Any | None = None
    raw_kind: str | None = None


class ObjectInspectorRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    object_key: str
    object_id: str
    object_name: str
    object_handle_text: str | None = None
    class_name: str = ""
    class_handle_text: str | None = None
    family: str = "generic"
    attributes: dict[str, Any] = Field(default_factory=dict)
    update_count: int = 0
    discovery_count: int = 0
    last_tag: Any | None = None
    sources: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)


class InteractionInspectorRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    interaction_key: str
    interaction_class: str
    class_handle_text: str | None = None
    family: str = "generic"
    source: str = ""
    observer_role: str | None = None
    tag: Any | None = None
    parameters: dict[str, Any] | None = None


class InspectorsPayload(BaseModel):
    objects: list[ObjectInspectorRow] = Field(default_factory=list)
    interactions: list[InteractionInspectorRow] = Field(default_factory=list)


class InspectorObjectsResponse(BaseModel):
    objects: list[ObjectInspectorRow]
    status: str


class InspectorInteractionsResponse(BaseModel):
    interactions: list[InteractionInspectorRow]
    status: str


class PluginPanelsResponse(BaseModel):
    plugin_panels: list[dict[str, Any]]
    status: str


class EventsResponse(BaseModel):
    events: list[dict[str, Any]]


class RuntimeObserverStateResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    provider: str | None = None
    scenario: str | None = None
    label: str | None = None
    story: str | None = None
    supports_live_callbacks: bool | None = None
    participant_profiles: list[dict[str, Any]] = Field(default_factory=list)
    backend: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)
    status: str
    error: str | None = None
    summary_ready: bool | None = None
    listener_report_ready: bool | None = None
    artifacts: dict[str, Any] = Field(default_factory=dict)
    live_metrics: dict[str, Any] = Field(default_factory=dict)
    final_summary: dict[str, Any] | None = None
    catalog_metadata: dict[str, Any] = Field(default_factory=dict)
    inspectors: InspectorsPayload = Field(default_factory=InspectorsPayload)
    plugin_panels: list[dict[str, Any]] = Field(default_factory=list)
    normalized_events: list[NormalizedEventRecord] = Field(default_factory=list)
    schema_version: str = RUNTIME_OBSERVER_EVENT_SCHEMA_VERSION


def _typed_state(control: RuntimeObserverControl) -> RuntimeObserverStateResponse:
    return RuntimeObserverStateResponse.model_validate(control.state())


def _html_escape(value: Any) -> str:
    text = str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


def render_runtime_subscriber_app_html(state: Mapping[str, Any]) -> str:
    initial_state = json.dumps(state, sort_keys=True)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Federation Visualizer</title>
  <style>
    :root {{
      --sand: #efe4d2;
      --paper: rgba(255, 251, 245, 0.88);
      --panel: rgba(255, 248, 239, 0.92);
      --ink: #1b2733;
      --muted: #5d6b78;
      --ember: #b54822;
      --ember-dark: #7d2f12;
      --teal: #1f6f78;
      --gold: #c48a24;
      --line: rgba(110, 85, 51, 0.18);
      --shadow: 0 20px 50px rgba(28, 25, 21, 0.14);
      --radius: 18px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at 15% 15%, rgba(196, 138, 36, 0.18), transparent 28%),
        radial-gradient(circle at 85% 10%, rgba(31, 111, 120, 0.14), transparent 24%),
        linear-gradient(145deg, #f5eee0 0%, #ece1cb 48%, #e7dbc6 100%);
      font: 15px/1.5 "Avenir Next", "Segoe UI", sans-serif;
      min-height: 100vh;
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: 0.28;
      background-image:
        linear-gradient(rgba(125, 47, 18, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(31, 111, 120, 0.03) 1px, transparent 1px);
      background-size: 36px 36px;
    }}
    main {{ max-width: 1460px; margin: 0 auto; padding: 28px 20px 56px; position: relative; }}
    .hero {{
      display: grid;
      grid-template-columns: 1.6fr 1fr;
      gap: 18px;
      margin-bottom: 18px;
      animation: rise 320ms ease-out;
    }}
    .card {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
    }}
    .hero-card {{ padding: 24px 24px 20px; overflow: hidden; position: relative; }}
    .hero-card::after {{
      content: "";
      position: absolute;
      right: -20px;
      top: -24px;
      width: 160px;
      height: 160px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(180, 72, 34, 0.18), transparent 70%);
    }}
    h1 {{
      margin: 0 0 8px;
      font: 700 34px/1.05 "Iowan Old Style", "Palatino Linotype", serif;
      letter-spacing: -0.03em;
      color: var(--ember-dark);
    }}
    h2 {{
      margin: 0 0 12px;
      font: 700 18px/1.2 "Iowan Old Style", "Palatino Linotype", serif;
      color: var(--ember-dark);
    }}
    .lede {{
      color: var(--muted);
      max-width: 60ch;
      margin: 0 0 18px;
    }}
    .hero-meta {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }}
    .pill {{
      padding: 12px 14px;
      border-radius: 14px;
      background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,247,236,0.82));
      border: 1px solid var(--line);
    }}
    .pill .label {{ display: block; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); }}
    .pill .value {{ display: block; margin-top: 4px; font: 700 18px/1.2 "IBM Plex Mono", "SFMono-Regular", monospace; }}
    .control-card {{ padding: 22px; }}
    .control-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    label {{
      display: block;
      font-size: 12px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 6px;
    }}
    input, select, button, textarea {{
      width: 100%;
      border-radius: 12px;
      border: 1px solid rgba(92, 77, 58, 0.18);
      background: rgba(255,255,255,0.86);
      color: var(--ink);
      padding: 11px 12px;
      font: 500 14px/1.4 "IBM Plex Mono", "SFMono-Regular", monospace;
    }}
    textarea {{ min-height: 92px; resize: vertical; }}
    button {{
      cursor: pointer;
      font-weight: 700;
      transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
    }}
    button:hover {{ transform: translateY(-1px); box-shadow: 0 10px 20px rgba(27,39,51,0.1); }}
    .primary {{
      background: linear-gradient(135deg, var(--ember), #d16627);
      color: #fff9f3;
      border-color: rgba(125, 47, 18, 0.35);
    }}
    .secondary {{
      background: linear-gradient(135deg, rgba(31,111,120,0.15), rgba(31,111,120,0.08));
    }}
    .toolbar {{
      display: grid;
      grid-template-columns: 1.3fr 1fr;
      gap: 18px;
      margin-bottom: 18px;
      animation: rise 420ms ease-out;
    }}
    .toolbar-card {{ padding: 20px; }}
    .filter-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 18px;
      animation: rise 520ms ease-out;
    }}
    .stack {{ display: grid; gap: 18px; }}
    .section-card {{ padding: 20px; }}
    .section-head {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }}
    .section-note {{ color: var(--muted); font-size: 13px; }}
    .list-shell {{
      border: 1px solid var(--line);
      border-radius: 16px;
      overflow: hidden;
      background: var(--panel);
    }}
    .list-head, .list-row {{
      display: grid;
      gap: 10px;
      align-items: start;
      padding: 12px 14px;
    }}
    .list-head {{
      font-size: 11px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
      border-bottom: 1px solid var(--line);
      background: rgba(255,255,255,0.44);
    }}
    .list-row {{
      border-bottom: 1px solid rgba(110,85,51,0.09);
      cursor: pointer;
    }}
    .list-row:last-child {{ border-bottom: 0; }}
    .list-row.active {{
      background: linear-gradient(90deg, rgba(180,72,34,0.09), rgba(31,111,120,0.05));
    }}
    .mono {{
      font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .event-grid .list-head, .event-grid .list-row {{ grid-template-columns: 86px 150px 120px 1fr; }}
    .object-grid .list-head, .object-grid .list-row {{ grid-template-columns: 140px 190px 1fr 90px; }}
    .interaction-grid .list-head, .interaction-grid .list-row {{ grid-template-columns: 140px 110px 1fr; }}
    .participant-grid .list-head, .participant-grid .list-row {{ grid-template-columns: 160px 160px 1fr 1fr; }}
    .detail-pane {{
      min-height: 260px;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: linear-gradient(180deg, rgba(255,255,255,0.64), rgba(255,247,236,0.82));
      padding: 14px;
      overflow: auto;
    }}
    .plugin-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 14px;
    }}
    .plugin-metric {{
      border-radius: 14px;
      padding: 14px;
      background: rgba(255,255,255,0.76);
      border: 1px solid var(--line);
    }}
    .status-running {{ color: var(--teal); }}
    .status-failed {{ color: var(--ember-dark); }}
    .status-complete {{ color: #2c5b2f; }}
    .footer {{
      margin-top: 20px;
      color: var(--muted);
      font-size: 13px;
      text-align: right;
    }}
    @media (max-width: 1100px) {{
      .hero, .toolbar, .layout {{ grid-template-columns: 1fr; }}
      .hero-meta, .filter-grid, .control-grid, .plugin-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 720px) {{
      main {{ padding: 18px 14px 36px; }}
      .hero-meta, .filter-grid, .control-grid, .plugin-grid {{ grid-template-columns: 1fr; }}
      .event-grid .list-head, .event-grid .list-row,
      .object-grid .list-head, .object-grid .list-row,
      .interaction-grid .list-head, .interaction-grid .list-row,
      .participant-grid .list-head, .participant-grid .list-row {{ grid-template-columns: 1fr; }}
    }}
    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(8px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <article class="card hero-card">
        <h1>Federation Visualizer</h1>
        <p class="lede">A generic observer surface for live HLA federation state, event history, object and interaction inspection, and semantic scenario panels over one shared observer core.</p>
        <div class="hero-meta">
          <div class="pill"><span class="label">Status</span><span class="value" id="status-chip">idle</span></div>
          <div class="pill"><span class="label">Provider</span><span class="value" id="provider-chip">n/a</span></div>
          <div class="pill"><span class="label">Scenario</span><span class="value" id="scenario-chip">n/a</span></div>
          <div class="pill"><span class="label">Schema</span><span class="value" id="schema-chip">{_html_escape(RUNTIME_OBSERVER_EVENT_SCHEMA_VERSION)}</span></div>
        </div>
      </article>
      <aside class="card control-card">
        <div class="section-head">
          <h2>Launch</h2>
          <span class="section-note">FastAPI + WebSocket subscriber</span>
        </div>
        <div class="control-grid">
          <div>
            <label for="scenario-select">Observer Lane</label>
            <select id="scenario-select"></select>
          </div>
          <div>
            <label for="backend-input">Backend Override</label>
            <input id="backend-input" placeholder="python1516e or python1516_2025">
          </div>
          <div>
            <label for="steps-input">Target Radar Steps</label>
            <input id="steps-input" type="number" min="1" placeholder="4">
          </div>
          <div>
            <label for="options-input">Extra Options JSON</label>
            <textarea id="options-input" placeholder='{{"edition":"2010","federation_name":"demo-fed","federate_name":"Observer1","fom_modules":["/abs/path/FOM.xml"]}}'></textarea>
          </div>
        </div>
        <div class="control-grid" style="margin-top:12px">
          <button id="start-btn" class="primary">Start Observer</button>
          <button id="stop-btn" class="secondary">Stop Observer</button>
        </div>
      </aside>
    </section>

    <section class="toolbar">
      <article class="card toolbar-card">
        <div class="section-head">
          <h2>Filters</h2>
          <span class="section-note">Narrow the generic subscriber views without relying on family plugins</span>
        </div>
        <div class="filter-grid">
          <div>
            <label for="family-filter">Family</label>
            <select id="family-filter"></select>
          </div>
          <div>
            <label for="class-filter">Class</label>
            <select id="class-filter"></select>
          </div>
          <div>
            <label for="event-type-filter">Event Type</label>
            <select id="event-type-filter"></select>
          </div>
        </div>
      </article>
      <article class="card toolbar-card">
        <div class="section-head">
          <h2>Run Facts</h2>
          <span class="section-note">Bounded API surface, not full HLA-over-HTTP</span>
        </div>
        <div class="detail-pane mono" id="summary-pane"></div>
      </article>
    </section>

    <section class="layout">
      <div class="stack">
        <article class="card section-card">
          <div class="section-head">
            <h2>Participants</h2>
            <span class="section-note">Observed or declared federate roles</span>
          </div>
          <div class="list-shell participant-grid">
            <div class="list-head"><div>Federate</div><div>Role</div><div>Publishes</div><div>Subscribes</div></div>
            <div id="participants-list"></div>
          </div>
        </article>

        <article class="card section-card">
          <div class="section-head">
            <h2>Federate Roster</h2>
            <span class="section-note">Live roster from the observer session and MOM-style discoveries when available</span>
          </div>
          <div class="detail-pane mono" id="roster-detail"></div>
        </article>

        <article class="card section-card">
          <div class="section-head">
            <h2>Event Timeline</h2>
            <span class="section-note">Live normalized feed</span>
          </div>
          <div class="list-shell event-grid">
            <div class="list-head"><div>Seq</div><div>Type</div><div>Family</div><div>Details</div></div>
            <div id="events-list"></div>
          </div>
        </article>
      </div>

      <div class="stack">
        <article class="card section-card">
          <div class="section-head">
            <h2>Object Instances</h2>
            <span class="section-note">Stable identity via handles and aliases</span>
          </div>
          <div class="list-shell object-grid">
            <div class="list-head"><div>Family</div><div>Class</div><div>Object</div><div>Updates</div></div>
            <div id="objects-list"></div>
          </div>
          <div class="detail-pane mono" id="object-detail" style="margin-top:12px"></div>
        </article>

        <article class="card section-card">
          <div class="section-head">
            <h2>Interactions</h2>
            <span class="section-note">Generic receive surface across providers</span>
          </div>
          <div class="list-shell interaction-grid">
            <div class="list-head"><div>Family</div><div>Source</div><div>Class</div></div>
            <div id="interactions-list"></div>
          </div>
          <div class="detail-pane mono" id="interaction-detail" style="margin-top:12px"></div>
        </article>

        <article class="card section-card">
          <div class="section-head">
            <h2>FOM Tree</h2>
            <span class="section-note">Loaded object and interaction class hierarchy plus datatype inventory</span>
          </div>
          <div class="detail-pane mono" id="fom-detail"></div>
        </article>

        <article class="card section-card">
          <div class="section-head">
            <h2>Semantic Panels</h2>
            <span class="section-note">Optional semantic overlay panels</span>
          </div>
          <div id="plugin-root"></div>
        </article>
      </div>
    </section>

    <div class="footer">API: <code>/api/health</code> <code>/api/catalog</code> <code>/api/schema</code> <code>/api/state</code> <code>/api/events</code> <code>/api/inspectors/*</code> <code>/api/control/*</code> <code>/ws/events</code></div>
  </main>
  <script>
    const initialState = {initial_state};
    const scenarioSelectEl = document.getElementById("scenario-select");
    const backendInputEl = document.getElementById("backend-input");
    const stepsInputEl = document.getElementById("steps-input");
    const optionsInputEl = document.getElementById("options-input");
    const familyFilterEl = document.getElementById("family-filter");
    const classFilterEl = document.getElementById("class-filter");
    const eventTypeFilterEl = document.getElementById("event-type-filter");
    const participantsListEl = document.getElementById("participants-list");
    const eventsListEl = document.getElementById("events-list");
    const objectsListEl = document.getElementById("objects-list");
    const interactionsListEl = document.getElementById("interactions-list");
    const objectDetailEl = document.getElementById("object-detail");
    const interactionDetailEl = document.getElementById("interaction-detail");
    const rosterDetailEl = document.getElementById("roster-detail");
    const fomDetailEl = document.getElementById("fom-detail");
    const summaryPaneEl = document.getElementById("summary-pane");
    const pluginRootEl = document.getElementById("plugin-root");
    const statusChipEl = document.getElementById("status-chip");
    const providerChipEl = document.getElementById("provider-chip");
    const scenarioChipEl = document.getElementById("scenario-chip");
    const schemaChipEl = document.getElementById("schema-chip");
    let catalog = null;
    let state = initialState;
    let objectIndex = 0;
    let interactionIndex = 0;
    let fomSearchFilter = "";
    let fomKindFilter = "all";
    let pinnedFomSymbol = null;
    let pinnedFomKind = null;
    let expandedFomNodes = new Set();

    function escapeHtml(value) {{
      return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }}

    function uniqueSorted(values) {{
      return Array.from(new Set(values.filter(Boolean))).sort((a, b) => a.localeCompare(b));
    }}

    function fillSelect(selectNode, values, currentValue, allLabel = "All") {{
      const options = ["all"].concat(values);
      selectNode.innerHTML = options.map((value) => `<option value="${{escapeHtml(value)}}">${{value === "all" ? allLabel : escapeHtml(value)}}</option>`).join("");
      selectNode.value = options.includes(currentValue) ? currentValue : "all";
    }}

    function activeFilters() {{
      return {{
        family: familyFilterEl.value || "all",
        className: classFilterEl.value || "all",
        eventType: eventTypeFilterEl.value || "all",
      }};
    }}

    function eventClassName(event) {{
      return event.class_name || event.interaction_class || "";
    }}

    function eventPassesFilters(event, filters) {{
      if (filters.family !== "all" && (event.family || "generic") !== filters.family) return false;
      if (filters.className !== "all" && eventClassName(event) !== filters.className) return false;
      if (filters.eventType !== "all" && (event.event_type || "") !== filters.eventType) return false;
      return true;
    }}

    function filteredObjects(payload, filters) {{
      return ((payload.inspectors && payload.inspectors.objects) || []).filter((row) => {{
        if (filters.family !== "all" && (row.family || "generic") !== filters.family) return false;
        if (filters.className !== "all" && (row.class_name || "") !== filters.className) return false;
        if (pinnedFomSymbol && (row.class_name || "") !== pinnedFomSymbol) return false;
        if (filters.eventType !== "all") {{
          const discovered = filters.eventType === "object.discovered" && (row.discovery_count || 0) > 0;
          const updated = filters.eventType === "object.updated" && (row.update_count || 0) > 0;
          if (!discovered && !updated) return false;
        }}
        return true;
      }});
    }}

    function filteredInteractions(payload, filters) {{
      return ((payload.inspectors && payload.inspectors.interactions) || []).filter((row) => {{
        if (filters.family !== "all" && (row.family || "generic") !== filters.family) return false;
        if (filters.className !== "all" && (row.interaction_class || "") !== filters.className) return false;
        if (pinnedFomSymbol && (row.interaction_class || "") !== pinnedFomSymbol) return false;
        if (filters.eventType !== "all" && filters.eventType !== "interaction.received") return false;
        return true;
      }});
    }}

    function renderCatalog() {{
      if (!catalog) return;
      const options = [];
      for (const provider of catalog.providers || []) {{
        for (const row of provider.scenarios || []) {{
          options.push(`<option value="${{escapeHtml(provider.provider)}}::${{escapeHtml(row.id)}}">${{escapeHtml(provider.label)}} :: ${{escapeHtml(row.label)}}</option>`);
        }}
      }}
      scenarioSelectEl.innerHTML = options.join("");
    }}

    function renderParticipants(rows) {{
      participantsListEl.innerHTML = rows.map((row) => `
        <div class="list-row">
          <div>${{escapeHtml(row.federate || "")}}</div>
          <div>${{escapeHtml(row.role || "")}}</div>
          <div class="mono">${{escapeHtml((row.publishes || []).join(", "))}}</div>
          <div class="mono">${{escapeHtml((row.subscribes || []).join(", "))}}</div>
        </div>
      `).join("") || `<div class="list-row"><div>No participants yet.</div><div></div><div></div><div></div></div>`;
    }}

    function renderEvents(rows) {{
      eventsListEl.innerHTML = rows.map((row) => `
        <div class="list-row">
          <div class="mono">${{escapeHtml(row.sequence ?? "")}}</div>
          <div>${{escapeHtml(row.event_type || "")}}</div>
          <div>${{escapeHtml(row.family || "generic")}}</div>
          <div class="mono">${{escapeHtml(JSON.stringify(row, null, 0))}}</div>
        </div>
      `).join("") || `<div class="list-row"><div>No events observed yet.</div><div></div><div></div><div></div></div>`;
    }}

    function renderObjects(rows) {{
      objectsListEl.innerHTML = rows.map((row, index) => `
        <div class="list-row ${{index === objectIndex ? "active" : ""}}" data-index="${{index}}">
          <div>${{escapeHtml(row.family || "generic")}}</div>
          <div>${{escapeHtml(row.class_name || "")}}</div>
          <div class="mono">${{escapeHtml(row.object_name || row.object_key || "")}}</div>
          <div class="mono">${{escapeHtml(row.update_count || 0)}}</div>
        </div>
      `).join("") || `<div class="list-row"><div>No objects observed yet.</div><div></div><div></div><div></div></div>`;
      for (const node of objectsListEl.querySelectorAll(".list-row[data-index]")) {{
        node.onclick = () => {{
          objectIndex = Number(node.dataset.index || "0");
          const selected = rows[Math.min(objectIndex, rows.length - 1)];
          if (selected && selected.class_name) pinFomSymbol(selected.class_name, "object");
          renderState();
        }};
      }}
      if (!rows.length) {{
        objectDetailEl.textContent = "No object selected.";
        return;
      }}
      const row = rows[Math.min(objectIndex, rows.length - 1)];
      objectDetailEl.textContent = JSON.stringify({{
        pinned_fom_symbol: pinnedFomSymbol,
        pinned_fom_kind: pinnedFomKind,
        row,
      }}, null, 2);
    }}

    function renderInteractions(rows) {{
      interactionsListEl.innerHTML = rows.map((row, index) => `
        <div class="list-row ${{index === interactionIndex ? "active" : ""}}" data-index="${{index}}">
          <div>${{escapeHtml(row.family || "generic")}}</div>
          <div>${{escapeHtml(row.source || "")}}</div>
          <div class="mono">${{escapeHtml(row.interaction_class || "")}}</div>
        </div>
      `).join("") || `<div class="list-row"><div>No interactions observed yet.</div><div></div><div></div></div>`;
      for (const node of interactionsListEl.querySelectorAll(".list-row[data-index]")) {{
        node.onclick = () => {{
          interactionIndex = Number(node.dataset.index || "0");
          const selected = rows[Math.min(interactionIndex, rows.length - 1)];
          if (selected && selected.interaction_class) pinFomSymbol(selected.interaction_class, "interaction");
          renderState();
        }};
      }}
      if (!rows.length) {{
        interactionDetailEl.textContent = "No interaction selected.";
        return;
      }}
      const row = rows[Math.min(interactionIndex, rows.length - 1)];
      interactionDetailEl.textContent = JSON.stringify({{
        pinned_fom_symbol: pinnedFomSymbol,
        pinned_fom_kind: pinnedFomKind,
        row,
      }}, null, 2);
    }}

    function renderPluginPanels(panels) {{
      if (!panels.length) {{
        pluginRootEl.innerHTML = `<div class="detail-pane mono">No scenario-specific panel active for this run.</div>`;
        return;
      }}
      const panel = panels[0];
      const metrics = [];
      if (panel.track_report_count != null) metrics.push(["Track Reports", panel.track_report_count]);
      if (panel.weapon_fire_count != null) metrics.push(["WeaponFire", panel.weapon_fire_count]);
      if (panel.detonation_count != null) metrics.push(["Detonations", panel.detonation_count]);
      if (panel.jtids_count != null) metrics.push(["JTIDS", panel.jtids_count]);
      if (panel.rttab_count != null) metrics.push(["RTTAB", panel.rttab_count]);
      if (panel.bridge_objects) metrics.push(["Bridge Objects", panel.bridge_objects.length]);
      if (panel.radio_objects) metrics.push(["Radio Objects", panel.radio_objects.length]);
      pluginRootEl.innerHTML = `
        <div class="plugin-grid">
          ${{metrics.map(([label, value]) => `<div class="plugin-metric"><div class="section-note">${{escapeHtml(label)}}</div><div class="mono" style="font-size:20px;margin-top:6px">${{escapeHtml(value)}}</div></div>`).join("")}}
        </div>
        <div class="detail-pane mono">${{escapeHtml(JSON.stringify(panel, null, 2))}}</div>
      `;
    }}

    function renderRoster(rows) {{
      rosterDetailEl.textContent = rows.length ? JSON.stringify(rows, null, 2) : "No federate roster entries observed yet.";
    }}

    function workbenchHref(target, row = null) {{
      if (!target) return null;
      const params = new URLSearchParams((target.fragment || "").replace(/^#/, ""));
      if (row && row.name) params.set("symbol", row.name);
      if (row && row.kind) params.set("kind", row.kind);
      return `/workbench/fom_workbench.html#${{params.toString()}}`;
    }}

    function pinFomSymbol(symbol, kind) {{
      pinnedFomSymbol = symbol || null;
      pinnedFomKind = kind || null;
      if (symbol && kind === "object") {{
        classFilterEl.value = symbol;
      }}
      if (symbol && kind === "interaction") {{
        classFilterEl.value = symbol;
      }}
      renderState();
    }}

    function clearPinnedFomSymbol() {{
      pinnedFomSymbol = null;
      pinnedFomKind = null;
      renderState();
    }}

    function toggleFomNode(symbol) {{
      if (!symbol) return;
      if (expandedFomNodes.has(symbol)) expandedFomNodes.delete(symbol);
      else expandedFomNodes.add(symbol);
      renderState();
    }}

    function renderFomTree(payload) {{
      const tree = payload.fom_tree || {{}};
      const loaded = payload.loaded_fom_set || null;
      const objectRowsLive = ((payload.inspectors && payload.inspectors.objects) || []);
      const interactionRowsLive = ((payload.inspectors && payload.inspectors.interactions) || []);
      const targets = loaded?.workbench_targets || [];
      const targetMap = new Map(targets.map((target) => [target.target_name || target.label, target]));
      const objectActivityCounts = new Map();
      const interactionActivityCounts = new Map();
      for (const row of objectRowsLive) {{
        const className = row.class_name || "";
        if (!className) continue;
        const current = objectActivityCounts.get(className) || {{ instances: 0, updates: 0, discoveries: 0 }};
        current.instances += 1;
        current.updates += Number(row.update_count || 0);
        current.discoveries += Number(row.discovery_count || 0);
        objectActivityCounts.set(className, current);
      }}
      for (const row of interactionRowsLive) {{
        const className = row.interaction_class || "";
        if (!className) continue;
        const current = interactionActivityCounts.get(className) || {{ receives: 0 }};
        current.receives += 1;
        interactionActivityCounts.set(className, current);
      }}
      const objectTreeRows = (tree.object_classes || []).map((row) => ({{ kind: "object", name: row.full_name, parent_name: row.parent_name, lineage: row.lineage || [], depth: row.depth || 0 }}));
      const interactionTreeRows = (tree.interaction_classes || []).map((row) => ({{ kind: "interaction", name: row.full_name, parent_name: row.parent_name, lineage: row.lineage || [], depth: row.depth || 0 }}));
      const objectChildren = new Map();
      const interactionChildren = new Map();
      for (const row of objectTreeRows) {{
        if (!row.parent_name) continue;
        const current = objectChildren.get(row.parent_name) || [];
        current.push(row.name);
        objectChildren.set(row.parent_name, current);
      }}
      for (const row of interactionTreeRows) {{
        if (!row.parent_name) continue;
        const current = interactionChildren.get(row.parent_name) || [];
        current.push(row.name);
        interactionChildren.set(row.parent_name, current);
      }}
      const objectRollupCounts = new Map();
      const interactionRollupCounts = new Map();
      for (const row of objectTreeRows) {{
        const direct = objectActivityCounts.get(row.name) || {{ instances: 0, updates: 0, discoveries: 0 }};
        for (const ancestor of (row.lineage || [])) {{
          const current = objectRollupCounts.get(ancestor) || {{ instances: 0, updates: 0, discoveries: 0 }};
          current.instances += direct.instances;
          current.updates += direct.updates;
          current.discoveries += direct.discoveries;
          objectRollupCounts.set(ancestor, current);
        }}
      }}
      for (const row of interactionTreeRows) {{
        const direct = interactionActivityCounts.get(row.name) || {{ receives: 0 }};
        for (const ancestor of (row.lineage || [])) {{
          const current = interactionRollupCounts.get(ancestor) || {{ receives: 0 }};
          current.receives += direct.receives;
          interactionRollupCounts.set(ancestor, current);
        }}
      }}
      const links = targets.map((target) => {{
        const href = workbenchHref(target);
        return `<div><a href="${{escapeHtml(href)}}" target="_blank" rel="noopener">${{escapeHtml(target.label || target.target_name || "Open in workbench")}}</a></div>`;
      }}).join("");
      const searchRows = Array.isArray(tree.search_index) ? tree.search_index : [];
      const filteredRows = searchRows.filter((row) => {{
        if (fomKindFilter !== "all" && (row.kind || "") !== fomKindFilter) return false;
        if (pinnedFomSymbol && row.name !== pinnedFomSymbol) return false;
        if (!fomSearchFilter) return true;
        const haystack = [
          row.name || "",
          row.parent_name || "",
          ...(row.lineage || []),
          ...(row.edition_classes || []),
          row.edition_scope || "",
          row.load_mode || "",
        ].join(" ").toLowerCase();
        return haystack.includes(fomSearchFilter.toLowerCase());
      }}).slice(0, 40);
      const rawTreeRows = [
        ...objectTreeRows,
        ...interactionTreeRows,
      ].filter((row) => {{
        if (fomKindFilter !== "all" && row.kind !== fomKindFilter) return false;
        if (pinnedFomSymbol && row.name !== pinnedFomSymbol) return false;
        if (!fomSearchFilter) return true;
        return [row.name, row.parent_name || "", ...(row.lineage || [])].join(" ").toLowerCase().includes(fomSearchFilter.toLowerCase());
      }});
      const treeRows = rawTreeRows.filter((row) => {{
        if (row.depth <= 0) return true;
        if (fomSearchFilter || pinnedFomSymbol) return true;
        return (row.lineage || []).slice(0, -1).every((ancestor) => expandedFomNodes.has(ancestor));
      }}).slice(0, 30);
      const summary = loaded ? {{
        scenario_families: loaded.scenario_families || [],
        edition_classes: loaded.edition_classes || [],
        edition_scope: loaded.edition_scope || null,
        baseline_kinds: loaded.baseline_kinds || [],
        load_modes: loaded.load_modes || [],
        default_load_sets: loaded.default_load_sets || [],
        record_ids: loaded.record_ids || [],
        member_paths: loaded.member_paths || [],
        tree_counts: {{
          object_classes: (tree.object_classes || []).length,
          interaction_classes: (tree.interaction_classes || []).length,
          datatypes: (tree.datatypes || []).length,
          search_rows: (tree.search_index || []).length,
        }},
      }} : tree;
      const rowMarkup = filteredRows.map((row) => {{
        const target = targetMap.get(row.source_name) || targets[0] || null;
        const href = workbenchHref(target, row);
        const pinned = pinnedFomSymbol && row.name === pinnedFomSymbol;
        return `
          <div class="list-row${{pinned ? " active" : ""}}">
            <div>${{escapeHtml(row.kind || "")}}</div>
            <div class="mono">${{escapeHtml(row.name || "")}}<br><span class="section-note">${{escapeHtml((row.lineage || []).join(" > "))}}</span></div>
            <div>
              <button type="button" class="symbol-pin-button" data-symbol="${{escapeHtml(row.name || "")}}" data-kind="${{escapeHtml(row.kind || "")}}">pin</button>
              ${{href ? `<a href="${{escapeHtml(href)}}" target="_blank" rel="noopener">open</a>` : "<span class='section-note'>n/a</span>"}}
            </div>
          </div>
        `;
      }}).join("") || `<div class="list-row"><div>No matching FOM symbols.</div><div></div><div></div></div>`;
      const treeMarkup = treeRows.map((row) => {{
        const target = targets[0] || null;
        const href = workbenchHref(target, row);
        const indent = Math.max(0, Number(row.depth || 0)) * 14;
        const childMap = row.kind === "object" ? objectChildren : interactionChildren;
        const hasChildren = childMap.has(row.name);
        const expanded = expandedFomNodes.has(row.name);
        const directActivity = row.kind === "object"
          ? (objectActivityCounts.get(row.name) || {{ instances: 0, updates: 0, discoveries: 0 }})
          : (interactionActivityCounts.get(row.name) || {{ receives: 0 }});
        const rollupActivity = row.kind === "object"
          ? (objectRollupCounts.get(row.name) || {{ instances: 0, updates: 0, discoveries: 0 }})
          : (interactionRollupCounts.get(row.name) || {{ receives: 0 }});
        const directLabel = row.kind === "object"
          ? `direct instances:${{directActivity.instances}} updates:${{directActivity.updates}} discoveries:${{directActivity.discoveries}}`
          : `direct receives:${{directActivity.receives}}`;
        const rollupLabel = row.kind === "object"
          ? `rollup instances:${{rollupActivity.instances}} updates:${{rollupActivity.updates}} discoveries:${{rollupActivity.discoveries}}`
          : `rollup receives:${{rollupActivity.receives}}`;
        const previewLabel = row.kind === "object"
          ? `preview objects:${{directActivity.instances}} descendants:${{Math.max(0, rollupActivity.instances - directActivity.instances)}}`
          : `preview receives:${{directActivity.receives}} descendants:${{Math.max(0, rollupActivity.receives - directActivity.receives)}}`;
        const pinned = pinnedFomSymbol && row.name === pinnedFomSymbol;
        return `
          <div class="list-row${{pinned ? " active" : ""}}">
            <div>${{escapeHtml(row.kind)}}</div>
            <div class="mono" style="padding-left:${{indent}}px">
              <span>${{hasChildren ? `<button type="button" class="tree-toggle-button" data-symbol="${{escapeHtml(row.name)}}">${{expanded ? "collapse" : "expand"}}</button>` : "<span class='section-note'>leaf</span>"}}</span>
              ${{escapeHtml(row.name)}}
              <br><span class="section-note">${{escapeHtml((row.lineage || []).join(" > "))}}</span>
              <br><span class="section-note">${{escapeHtml(directLabel)}}</span>
              <br><span class="section-note">${{escapeHtml(rollupLabel)}}</span>
              <br><span class="section-note">${{escapeHtml(previewLabel)}}</span>
            </div>
            <div>
              <button type="button" class="tree-pin-button" data-symbol="${{escapeHtml(row.name)}}" data-kind="${{escapeHtml(row.kind)}}">pin</button>
              ${{href ? `<a href="${{escapeHtml(href)}}" target="_blank" rel="noopener">open</a>` : "<span class='section-note'>n/a</span>"}}
            </div>
          </div>
        `;
      }}).join("") || `<div class="list-row"><div>No matching tree rows.</div><div></div><div></div></div>`;
      fomDetailEl.innerHTML = `
        <div style="margin-bottom:12px;">
          <div class="section-note">Workbench Links</div>
          ${{links || "<div class='mono'>No workbench links available for this run.</div>"}}
        </div>
        <div style="margin-bottom:12px;">
          <div class="section-note">Pinned Symbol</div>
          <div class="mono">${{pinnedFomSymbol ? escapeHtml(`${{pinnedFomKind || "symbol"}}: ${{pinnedFomSymbol}}`) : "none"}}</div>
          <div style="margin-top:8px;"><button type="button" id="clear-fom-pin">clear pin</button></div>
        </div>
        <div style="margin-bottom:12px;">
          <div class="section-note">FOM Search</div>
          <div style="display:grid;grid-template-columns:1fr 180px;gap:10px;margin-top:8px;">
            <input id="fom-search-input" type="search" placeholder="Search classes, interactions, datatypes" value="${{escapeHtml(fomSearchFilter)}}">
            <select id="fom-kind-filter">
              <option value="all"${{fomKindFilter === "all" ? " selected" : ""}}>all kinds</option>
              <option value="object"${{fomKindFilter === "object" ? " selected" : ""}}>objects</option>
              <option value="interaction"${{fomKindFilter === "interaction" ? " selected" : ""}}>interactions</option>
              <option value="datatype"${{fomKindFilter === "datatype" ? " selected" : ""}}>datatypes</option>
            </select>
          </div>
          <div class="list-shell" style="margin-top:10px;">
            <div class="list-head"><div>Kind</div><div>Symbol</div><div>Workbench</div></div>
            <div id="fom-search-results">${{rowMarkup}}</div>
          </div>
        </div>
        <div style="margin-bottom:12px;">
          <div class="section-note">FOM Tree Rows</div>
          <div class="list-shell" style="margin-top:10px;">
            <div class="list-head"><div>Kind</div><div>Hierarchy</div><div>Actions</div></div>
            <div id="fom-tree-results">${{treeMarkup}}</div>
          </div>
        </div>
        <div class="mono">${{escapeHtml(JSON.stringify(summary, null, 2))}}</div>
      `;
      const searchInput = document.getElementById("fom-search-input");
      const kindSelect = document.getElementById("fom-kind-filter");
      if (searchInput) {{
        searchInput.addEventListener("input", (event) => {{
          fomSearchFilter = event.target.value || "";
          renderFomTree(payload);
        }});
      }}
      if (kindSelect) {{
        kindSelect.addEventListener("change", (event) => {{
          fomKindFilter = event.target.value || "all";
          renderFomTree(payload);
        }});
      }}
      const clearPin = document.getElementById("clear-fom-pin");
      if (clearPin) {{
        clearPin.addEventListener("click", () => {{
          clearPinnedFomSymbol();
        }});
      }}
      fomDetailEl.querySelectorAll(".symbol-pin-button,.tree-pin-button").forEach((node) => {{
        node.addEventListener("click", () => {{
          pinFomSymbol(node.getAttribute("data-symbol") || "", node.getAttribute("data-kind") || "");
        }});
      }});
      fomDetailEl.querySelectorAll(".tree-toggle-button").forEach((node) => {{
        node.addEventListener("click", () => {{
          toggleFomNode(node.getAttribute("data-symbol") || "");
        }});
      }});
    }}

    function renderSummary(payload) {{
      const statusClass = payload.status ? `status-${{payload.status}}` : "";
      statusChipEl.className = `value ${{statusClass}}`;
      statusChipEl.textContent = payload.status || "idle";
      providerChipEl.textContent = payload.provider || "n/a";
      scenarioChipEl.textContent = payload.scenario || "n/a";
      schemaChipEl.textContent = payload.schema_version || "{_html_escape(RUNTIME_OBSERVER_EVENT_SCHEMA_VERSION)}";
      summaryPaneEl.textContent = JSON.stringify({{
        label: payload.label,
        story: payload.story,
        backend: payload.backend,
        options: payload.options,
        live_metrics: payload.live_metrics,
        artifacts: payload.artifacts,
        history_event_count: payload.history_event_count,
      }}, null, 2);
    }}

    function renderState() {{
      const payload = state || {{ status: "idle", normalized_events: [] }};
      renderSummary(payload);
      renderParticipants(payload.participant_profiles || []);
      renderRoster(payload.federate_roster || []);
      renderFomTree(payload);
      const events = payload.normalized_events || [];
      fillSelect(familyFilterEl, uniqueSorted(events.map((row) => row.family || "generic")), familyFilterEl.value || "all");
      fillSelect(classFilterEl, uniqueSorted(events.map((row) => eventClassName(row))), classFilterEl.value || "all");
      fillSelect(eventTypeFilterEl, uniqueSorted(events.map((row) => row.event_type || "")), eventTypeFilterEl.value || "all", "All Types");
      const filters = activeFilters();
      const filteredEventRows = events.filter((row) => eventPassesFilters(row, filters));
      const objectRows = filteredObjects(payload, filters);
      const interactionRows = filteredInteractions(payload, filters);
      objectIndex = Math.min(objectIndex, Math.max(objectRows.length - 1, 0));
      interactionIndex = Math.min(interactionIndex, Math.max(interactionRows.length - 1, 0));
      renderEvents(filteredEventRows);
      renderObjects(objectRows);
      renderInteractions(interactionRows);
      renderPluginPanels(payload.plugin_panels || []);
    }}

    async function refreshCatalog() {{
      const response = await fetch("/api/catalog", {{ cache: "no-store" }});
      catalog = await response.json();
      renderCatalog();
    }}

    async function refreshState() {{
      const response = await fetch("/api/state", {{ cache: "no-store" }});
      state = await response.json();
      renderState();
    }}

    function parseOptions() {{
      const payload = optionsInputEl.value.trim();
      let options = {{}};
      if (payload) options = JSON.parse(payload);
      if (stepsInputEl.value) options.target_radar_steps = Number(stepsInputEl.value);
      return options;
    }}

    async function startScenario() {{
      const [provider, scenario] = (scenarioSelectEl.value || "").split("::");
      const response = await fetch("/api/control/start", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{
          provider,
          scenario,
          backend: backendInputEl.value || null,
          options: parseOptions(),
        }}),
      }});
      if (!response.ok) {{
        const failure = await response.json();
        alert(failure.detail || JSON.stringify(failure));
        return;
      }}
      state = await response.json();
      renderState();
    }}

    async function stopScenario() {{
      const response = await fetch("/api/control/stop", {{ method: "POST" }});
      state = await response.json();
      renderState();
    }}

    function connectSocket() {{
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const socket = new WebSocket(`${{protocol}}://${{window.location.host}}/ws/events`);
      socket.onmessage = async () => {{
        await refreshState();
      }};
      socket.onclose = () => {{
        window.setTimeout(connectSocket, 1200);
      }};
      socket.onerror = () => socket.close();
    }}

    document.getElementById("start-btn").onclick = () => startScenario();
    document.getElementById("stop-btn").onclick = () => stopScenario();
    familyFilterEl.onchange = () => renderState();
    classFilterEl.onchange = () => renderState();
    eventTypeFilterEl.onchange = () => renderState();

    refreshCatalog().then(() => refreshState());
    connectSocket();
    window.setInterval(refreshState, 5000);
  </script>
</body>
</html>
"""


def create_runtime_observer_fastapi_app(control: RuntimeObserverControl) -> FastAPI:
    app = FastAPI(
        title="Federation Visualizer API",
        version=RUNTIME_OBSERVER_EVENT_SCHEMA_VERSION,
        description="Generic FastAPI observer and control surface for live HLA federation visualization lanes.",
    )
    workbench_root = _repo_root() / "artifacts" / "fom_workbench"
    workbench_root.mkdir(parents=True, exist_ok=True)
    if not (workbench_root / "fom_workbench.html").exists():
        try:
            write_fom_workbench_html(output_dir=workbench_root)
        except Exception:
            pass
    app.mount("/workbench", StaticFiles(directory=str(workbench_root)), name="workbench")

    @app.get("/", response_class=HTMLResponse)
    async def index() -> str:
        return render_runtime_subscriber_app_html(control.state())

    @app.get("/api/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        session = control.current_session()
        return HealthResponse(
            service="federation-visualizer",
            status="ok",
            schema_version=RUNTIME_OBSERVER_EVENT_SCHEMA_VERSION,
            session_active=session is not None,
        )

    @app.get("/api/catalog")
    async def catalog() -> dict[str, Any]:
        return build_runtime_observer_catalog()

    @app.get("/api/schema")
    async def schema() -> dict[str, Any]:
        return build_runtime_observer_event_schema()

    @app.get("/api/state", response_model=RuntimeObserverStateResponse)
    async def state() -> RuntimeObserverStateResponse:
        return _typed_state(control)

    @app.get("/api/events", response_model=EventsResponse)
    async def events(after: int = 0) -> EventsResponse:
        return EventsResponse(events=control.events(after_sequence=after))

    @app.get("/api/inspectors/objects", response_model=InspectorObjectsResponse)
    async def objects() -> InspectorObjectsResponse:
        state = _typed_state(control)
        return InspectorObjectsResponse(objects=state.inspectors.objects, status=state.status)

    @app.get("/api/inspectors/interactions", response_model=InspectorInteractionsResponse)
    async def interactions() -> InspectorInteractionsResponse:
        state = _typed_state(control)
        return InspectorInteractionsResponse(interactions=state.inspectors.interactions, status=state.status)

    @app.get("/api/plugin-panels", response_model=PluginPanelsResponse)
    async def plugin_panels() -> PluginPanelsResponse:
        state = _typed_state(control)
        return PluginPanelsResponse(plugin_panels=state.plugin_panels, status=state.status)

    @app.post("/api/control/start", response_model=RuntimeObserverStateResponse)
    async def start(request: ObserverStartRequest) -> RuntimeObserverStateResponse:
        try:
            session = control.start(
                provider=request.provider,
                scenario=request.scenario,
                backend=request.backend,
                options=request.options,
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=repr(exc)) from exc
        return RuntimeObserverStateResponse.model_validate(session.live_state())

    @app.post("/api/control/stop", response_model=ObserverStopResponse | RuntimeObserverStateResponse)
    async def stop() -> ObserverStopResponse | RuntimeObserverStateResponse:
        payload = control.stop()
        if set(payload.keys()) == {"status"}:
            return ObserverStopResponse.model_validate(payload)
        return RuntimeObserverStateResponse.model_validate(payload)

    @app.get("/api/events/stream")
    async def event_stream() -> StreamingResponse:
        async def _publisher():
            after = 0
            while True:
                events = control.events(after_sequence=after)
                for event in events:
                    after = int(event.get("sequence", after))
                    yield f"data: {json.dumps(event, sort_keys=True)}\n\n"
                await asyncio.sleep(0.5)

        return StreamingResponse(_publisher(), media_type="text/event-stream")

    @app.websocket("/ws/events")
    async def websocket_events(socket: WebSocket) -> None:
        await socket.accept()
        after = 0
        try:
            while True:
                events = control.events(after_sequence=after)
                for event in events:
                    after = int(event.get("sequence", after))
                    await socket.send_json(event)
                await asyncio.sleep(0.5)
        except WebSocketDisconnect:
            return

    return app


def build_runtime_observer_fastapi_app(
    *,
    output_dir: str | Path,
    backend: str | None = None,
    provider: str | None = None,
    scenario: str | None = None,
) -> FastAPI:
    control = RuntimeObserverControl(output_dir=output_dir, default_backend=backend)
    if provider is not None and scenario is not None:
        control.start(provider=provider, scenario=scenario, backend=backend)
    return create_runtime_observer_fastapi_app(control)


__all__ = [
    "ObserverStartRequest",
    "ObserverStopResponse",
    "build_runtime_observer_fastapi_app",
    "create_runtime_observer_fastapi_app",
    "render_runtime_subscriber_app_html",
]
