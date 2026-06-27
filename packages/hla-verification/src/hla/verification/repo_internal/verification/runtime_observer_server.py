"""Legacy local HTTP/SSE transport wrapper over the reusable runtime observer core."""
from __future__ import annotations

import json
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .runtime_observer_core import (
    LiveRuntimeObserverSession,
    RUNTIME_OBSERVER_EVENT_SCHEMA_VERSION,
    RuntimeObserverControl,
    RuntimeObserverSession,
    _derive_generic_inspectors,
    _derive_link16_plugin,
    _derive_rpr_plugin,
    _derive_target_radar_plugin,
    _normalize_event,
    build_runtime_observer_catalog,
    build_runtime_observer_event_schema,
)


def _json_response(handler: BaseHTTPRequestHandler, payload: Any, *, status: HTTPStatus = HTTPStatus.OK) -> None:
    body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    handler.send_response(status.value)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def _html_response(handler: BaseHTTPRequestHandler, body: str, *, status: HTTPStatus = HTTPStatus.OK) -> None:
    payload = body.encode("utf-8")
    handler.send_response(status.value)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(payload)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(payload)


def _read_json_body(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0"))
    if length <= 0:
        return {}
    payload = handler.rfile.read(length)
    if not payload:
        return {}
    return json.loads(payload.decode("utf-8"))


def _html_escape(value: Any) -> str:
    text = str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def render_runtime_observer_html(control: RuntimeObserverControl, state: dict[str, Any]) -> str:
    providers = control.catalog()["providers"]
    option_rows = []
    for provider in providers:
        for row in provider["scenarios"]:
            option_rows.append(
                f'<option value="{_html_escape(provider["provider"])}::{_html_escape(row["id"])}">'
                f'{_html_escape(provider["label"])} :: {_html_escape(row["label"])}'
                "</option>"
            )
    participants = "\n".join(
        "<tr>"
        f"<td>{_html_escape(row['federate'])}</td>"
        f"<td>{_html_escape(row['role'])}</td>"
        f"<td>{_html_escape(row.get('posture', ''))}</td>"
        f"<td>{_html_escape(', '.join(row.get('publishes', [])))}</td>"
        f"<td>{_html_escape(', '.join(row.get('subscribes', [])))}</td>"
        "</tr>"
        for row in state.get("participant_profiles", [])
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Federation Visualizer</title>
  <style>
    :root {{
      --bg: #f3ecdf;
      --panel: #fffdfa;
      --ink: #1f2933;
      --accent: #9f3a16;
      --grid: #d7cbb8;
    }}
    body {{ margin: 0; font: 15px/1.5 Menlo, Consolas, monospace; background: radial-gradient(circle at top, #fff2d9, var(--bg)); color: var(--ink); }}
    main {{ max-width: 1320px; margin: 0 auto; padding: 24px; }}
    section {{ background: var(--panel); border: 1px solid var(--grid); border-radius: 16px; padding: 16px 18px; margin-bottom: 18px; }}
    h1, h2 {{ margin: 0 0 12px; }}
    h1 {{ color: var(--accent); }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid var(--grid); padding: 8px 10px; text-align: left; vertical-align: top; }}
    .stats {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }}
    .stat {{ border: 1px solid var(--grid); border-radius: 12px; padding: 12px; background: #fff8ef; }}
    code, pre, select, input, button {{ font: inherit; }}
    #event-log {{ max-height: 420px; overflow: auto; border: 1px solid var(--grid); border-radius: 12px; padding: 12px; background: #fff8ef; }}
    .controls {{ display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }}
    .controls button {{ padding: 8px 12px; border: 1px solid var(--grid); border-radius: 10px; background: #fff8ef; cursor: pointer; }}
    .plugin-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .plugin-card {{ border: 1px solid var(--grid); border-radius: 12px; padding: 12px; background: #fff8ef; }}
    .filter-bar {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-bottom: 12px; }}
  </style>
</head>
<body>
  <main>
    <section>
      <h1>Federation Visualizer</h1>
      <div class="controls">
        <select id="scenario-select">{''.join(option_rows)}</select>
        <input id="backend-input" placeholder="backend override (optional)" />
        <input id="steps-input" type="number" min="1" placeholder="target_radar_steps" />
        <button id="start-btn">Start</button>
        <button id="stop-btn">Stop</button>
      </div>
    </section>
    <section>
      <h2>Run State</h2>
      <div class="stats">
        <div class="stat"><strong>Status</strong><br><span id="status">{_html_escape(state.get('status', 'idle'))}</span></div>
        <div class="stat"><strong>Provider</strong><br><span id="provider">{_html_escape(state.get('provider', ''))}</span></div>
        <div class="stat"><strong>Scenario</strong><br><span id="scenario">{_html_escape(state.get('scenario', ''))}</span></div>
        <div class="stat"><strong>Events</strong><br><span id="event-count">0</span></div>
      </div>
      <p id="headline"></p>
      <p>Schema: <code id="schema-version">{_html_escape(state.get('schema_version', RUNTIME_OBSERVER_EVENT_SCHEMA_VERSION))}</code> via <code>/api/schema</code></p>
      <pre id="artifacts"></pre>
    </section>
    <section>
      <h2>Filters</h2>
      <div class="filter-bar">
        <label>Family<br><select id="family-filter"></select></label>
        <label>Class<br><select id="class-filter"></select></label>
        <label>Event Type<br><select id="event-type-filter"></select></label>
      </div>
    </section>
    <section>
      <h2>Participants</h2>
      <table>
        <thead><tr><th>Federate</th><th>Role</th><th>Posture</th><th>Publishes</th><th>Subscribes</th></tr></thead>
        <tbody id="participants">{participants}</tbody>
      </table>
    </section>
    <section>
      <h2>Object Inspector</h2>
      <div class="controls">
        <select id="object-select"></select>
      </div>
      <pre id="object-inspector"></pre>
    </section>
    <section>
      <h2>Interaction Inspector</h2>
      <div class="controls">
        <select id="interaction-select"></select>
      </div>
      <pre id="interaction-inspector"></pre>
    </section>
    <section id="plugin-panel" style="display:none">
      <h2 id="plugin-title">Scenario Plugin</h2>
      <pre id="plugin-body"></pre>
    </section>
    <section>
      <h2>Event Stream</h2>
      <div id="event-log"></div>
    </section>
  </main>
  <script>
    const eventLog = document.getElementById("event-log");
    const statusEl = document.getElementById("status");
    const providerEl = document.getElementById("provider");
    const scenarioEl = document.getElementById("scenario");
    const eventCountEl = document.getElementById("event-count");
    const headlineEl = document.getElementById("headline");
    const artifactsEl = document.getElementById("artifacts");
    const participantsEl = document.getElementById("participants");
    const objectSelectEl = document.getElementById("object-select");
    const objectInspectorEl = document.getElementById("object-inspector");
    const interactionSelectEl = document.getElementById("interaction-select");
    const interactionInspectorEl = document.getElementById("interaction-inspector");
    const pluginPanelEl = document.getElementById("plugin-panel");
    const pluginTitleEl = document.getElementById("plugin-title");
    const pluginBodyEl = document.getElementById("plugin-body");
    const selectEl = document.getElementById("scenario-select");
    const backendEl = document.getElementById("backend-input");
    const stepsEl = document.getElementById("steps-input");
    const familyFilterEl = document.getElementById("family-filter");
    const classFilterEl = document.getElementById("class-filter");
    const eventTypeFilterEl = document.getElementById("event-type-filter");
    let lastPayload = null;

    function renderParticipants(rows) {{
      participantsEl.innerHTML = rows.map((row) =>
        `<tr><td>${{row.federate || ""}}</td><td>${{row.role || ""}}</td><td>${{row.posture || ""}}</td><td>${{(row.publishes || []).join(", ")}}</td><td>${{(row.subscribes || []).join(", ")}}</td></tr>`
      ).join("");
    }}

    function uniqueSorted(values) {{
      return Array.from(new Set(values.filter(Boolean))).sort((left, right) => left.localeCompare(right));
    }}

    function renderFilterOptions(selectNode, values, currentValue) {{
      const options = ["all"].concat(values);
      selectNode.innerHTML = options.map((value) =>
        `<option value="${{value}}">${{value === "all" ? "All" : value}}</option>`
      ).join("");
      selectNode.value = options.includes(currentValue) ? currentValue : "all";
    }}

    function activeFilters() {{
      return {{
        family: familyFilterEl.value || "all",
        className: classFilterEl.value || "all",
        eventType: eventTypeFilterEl.value || "all",
      }};
    }}

    function eventPassesFilters(event, filters) {{
      const family = event.family || "generic";
      const className = event.class_name || event.interaction_class || "";
      if (filters.family !== "all" && family !== filters.family) return false;
      if (filters.className !== "all" && className !== filters.className) return false;
      if (filters.eventType !== "all" && (event.event_type || "") !== filters.eventType) return false;
      return true;
    }}

    function renderInspectorOptions(selectNode, rows, labelKey) {{
      selectNode.innerHTML = rows.map((row, index) =>
        `<option value="${{index}}">${{row[labelKey] || row.object_id || row.interaction_key || row.interaction_class || ("item-" + index)}}</option>`
      ).join("");
    }}

    function renderPluginPanel(panel) {{
      if (!panel) return "";
      return `<pre>${{JSON.stringify(panel, null, 2)}}</pre>`;
    }}

    function renderState(payload) {{
      lastPayload = payload;
      statusEl.textContent = payload.status;
      providerEl.textContent = payload.provider || "";
      scenarioEl.textContent = payload.scenario || "";
      eventCountEl.textContent = String(payload.live_metrics ? payload.live_metrics.event_count : 0);
      headlineEl.textContent = payload.story || "";
      artifactsEl.textContent = JSON.stringify(payload.artifacts || {{}}, null, 2);
      renderParticipants(payload.participant_profiles || []);
      const normalizedEvents = payload.normalized_events || [];
      const eventFamilies = uniqueSorted(normalizedEvents.map((row) => row.family || "generic"));
      const eventClasses = uniqueSorted(normalizedEvents.map((row) => row.class_name || row.interaction_class || ""));
      const eventTypes = uniqueSorted(normalizedEvents.map((row) => row.event_type || ""));
      renderFilterOptions(familyFilterEl, eventFamilies, familyFilterEl.value || "all");
      renderFilterOptions(classFilterEl, eventClasses, classFilterEl.value || "all");
      renderFilterOptions(eventTypeFilterEl, eventTypes, eventTypeFilterEl.value || "all");
      const filters = activeFilters();
      const filteredEvents = normalizedEvents.filter((row) => eventPassesFilters(row, filters));
      const objects = ((payload.inspectors && payload.inspectors.objects) || []).filter((row) => {{
        if (filters.family !== "all" && (row.family || "generic") !== filters.family) return false;
        if (filters.className !== "all" && (row.class_name || "") !== filters.className) return false;
        if (filters.eventType !== "all") {{
          const wantsDiscovery = filters.eventType === "object.discovered" && (row.discovery_count || 0) > 0;
          const wantsUpdate = filters.eventType === "object.updated" && (row.update_count || 0) > 0;
          if (!wantsDiscovery && !wantsUpdate) return false;
        }}
        return true;
      }});
      const interactions = ((payload.inspectors && payload.inspectors.interactions) || []).filter((row) => {{
        if (filters.family !== "all" && (row.family || "generic") !== filters.family) return false;
        if (filters.className !== "all" && (row.interaction_class || "") !== filters.className) return false;
        if (filters.eventType !== "all" && filters.eventType !== "interaction.received") return false;
        return true;
      }});
      renderInspectorOptions(objectSelectEl, objects, "object_name");
      renderInspectorOptions(interactionSelectEl, interactions, "interaction_class");
      objectInspectorEl.textContent = objects.length ? JSON.stringify(objects[0], null, 2) : "No object instances observed yet.";
      interactionInspectorEl.textContent = interactions.length ? JSON.stringify(interactions[0], null, 2) : "No interactions observed yet.";
      eventLog.innerHTML = filteredEvents.map((event) => `<pre>${{JSON.stringify(event, null, 2)}}</pre>`).join("");
      const plugins = payload.plugin_panels || [];
      if (plugins.length) {{
        pluginPanelEl.style.display = "";
        pluginTitleEl.textContent = plugins[0].title || "Scenario Plugin";
        pluginBodyEl.innerHTML = renderPluginPanel(plugins[0]);
      }} else {{
        pluginPanelEl.style.display = "none";
        pluginBodyEl.innerHTML = "";
      }}
    }}

    async function refreshState() {{
      const response = await fetch("/api/state", {{ cache: "no-store" }});
      renderState(await response.json());
    }}

    document.getElementById("start-btn").onclick = async () => {{
      const [provider, scenario] = selectEl.value.split("::");
      eventLog.innerHTML = "";
      await fetch("/api/control/start", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{
          provider,
          scenario,
          backend: backendEl.value || null,
          options: stepsEl.value ? {{ target_radar_steps: Number(stepsEl.value) }} : {{}}
        }})
      }});
      await refreshState();
    }};

    document.getElementById("stop-btn").onclick = async () => {{
      await fetch("/api/control/stop", {{ method: "POST" }});
      await refreshState();
    }};

    objectSelectEl.onchange = async () => refreshState();
    interactionSelectEl.onchange = async () => refreshState();
    familyFilterEl.onchange = async () => refreshState();
    classFilterEl.onchange = async () => refreshState();
    eventTypeFilterEl.onchange = async () => refreshState();

    refreshState();
    const source = new EventSource("/events");
    source.onmessage = async () => {{
      await refreshState();
    }};
    source.onerror = async () => {{
      await refreshState();
    }};
  </script>
</body>
</html>
"""


def serve_runtime_observer(
    *,
    scenario: str | None = None,
    provider: str = "siso-runtime",
    output_dir: str | Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    backend: str | None = None,
) -> RuntimeObserverControl:
    control = RuntimeObserverControl(output_dir=output_dir, default_backend=backend)
    if scenario is not None:
        control.start(provider=provider, scenario=scenario, backend=backend)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/":
                _html_response(self, render_runtime_observer_html(control, control.state()))
                return
            if parsed.path == "/api/catalog":
                _json_response(self, control.catalog())
                return
            if parsed.path == "/api/state":
                _json_response(self, control.state())
                return
            if parsed.path == "/api/schema":
                _json_response(self, build_runtime_observer_event_schema())
                return
            if parsed.path == "/api/events":
                query = parse_qs(parsed.query)
                after = int(query.get("after", ["0"])[0])
                _json_response(self, {"events": control.events(after_sequence=after)})
                return
            if parsed.path == "/events":
                self.send_response(HTTPStatus.OK.value)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Connection", "keep-alive")
                self.end_headers()
                after = 0
                while True:
                    events = control.events(after_sequence=after)
                    for event in events:
                        after = int(event.get("sequence", after))
                        payload = json.dumps(event, sort_keys=True)
                        self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                        self.wfile.flush()
                    time.sleep(0.5)
                return
            _json_response(self, {"error": "not-found", "path": parsed.path}, status=HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/api/control/start":
                payload = _read_json_body(self)
                try:
                    session = control.start(
                        provider=str(payload["provider"]),
                        scenario=str(payload["scenario"]),
                        backend=payload.get("backend"),
                        options=payload.get("options"),
                    )
                except Exception as exc:  # noqa: BLE001
                    _json_response(self, {"error": repr(exc)}, status=HTTPStatus.BAD_REQUEST)
                    return
                _json_response(self, session.live_state())
                return
            if parsed.path == "/api/control/stop":
                _json_response(self, control.stop())
                return
            _json_response(self, {"error": "not-found", "path": parsed.path}, status=HTTPStatus.NOT_FOUND)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

    server = ThreadingHTTPServer((host, port), Handler)
    try:
        server.serve_forever()
    finally:
        server.server_close()
    return control


__all__ = [
    "LiveRuntimeObserverSession",
    "RUNTIME_OBSERVER_EVENT_SCHEMA_VERSION",
    "RuntimeObserverControl",
    "RuntimeObserverSession",
    "_derive_generic_inspectors",
    "_derive_link16_plugin",
    "_derive_rpr_plugin",
    "_derive_target_radar_plugin",
    "_normalize_event",
    "build_runtime_observer_catalog",
    "build_runtime_observer_event_schema",
    "render_runtime_observer_html",
    "serve_runtime_observer",
]
