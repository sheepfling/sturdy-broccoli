"""Scenario-aware surface matrix for SISO runtime showcase rows."""
from __future__ import annotations

import csv
import html
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib import request

from fastapi.testclient import TestClient

from .federate_service_fastapi import create_federate_service_fastapi_app
from .runtime_observer_fastapi import build_runtime_observer_fastapi_app
from .siso_runtime_showcase import load_siso_runtime_showcase_manifest, run_siso_runtime_showcase_scenario
from .ui_surface_capture import (
    capture_live_federate_service,
    capture_live_visualizer,
    launch_browser,
    run_local_app,
    write_gallery_index,
    write_gallery_manifest,
)

SURFACE_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "surface_profile": "runtime-only",
        "includes_observer_api": False,
        "includes_visualizer_html": False,
        "includes_federate_service_api": False,
        "capture_kind": "listener-artifacts-only",
        "capture_recommended": False,
    },
    {
        "surface_profile": "observer-visualizer",
        "includes_observer_api": True,
        "includes_visualizer_html": True,
        "includes_federate_service_api": False,
        "capture_kind": "observer-api-plus-visualizer",
        "capture_recommended": True,
    },
    {
        "surface_profile": "observer-visualizer-bridge",
        "includes_observer_api": True,
        "includes_visualizer_html": True,
        "includes_federate_service_api": True,
        "capture_kind": "observer-api-visualizer-plus-bridge",
        "capture_recommended": True,
    },
)

SURFACE_MATRIX_PRESETS: dict[str, dict[str, Any]] = {
    "micro-bridge-smoke": {
        "description": "Smallest fully hydrated bridge lane across the SISO families for both editions.",
        "families": ["link16", "rpr", "space"],
        "editions": ["2010", "2025"],
        "topologies": ["micro-2"],
        "surface_profiles": ["observer-visualizer-bridge"],
    },
    "showcase-hydrated": {
        "description": "Hydrated visualizer rows across the larger 5- and 10-federate showcase topologies.",
        "families": ["link16", "rpr", "space"],
        "editions": ["2010", "2025"],
        "topologies": ["squad-5", "constellation-10"],
        "surface_profiles": ["observer-visualizer"],
    },
    "heaviest-interesting": {
        "description": "Heaviest interesting hydrated rows: Link16, RPR, and Space over the 10-federate constellation topology.",
        "families": ["link16", "rpr", "space"],
        "editions": ["2010", "2025"],
        "topologies": ["constellation-10"],
        "surface_profiles": ["observer-visualizer"],
    },
    "stress-mixed": {
        "description": "Mixed runtime-only plus hydrated observer coverage over the larger showcase rows.",
        "families": ["link16", "rpr", "space"],
        "editions": ["2010", "2025"],
        "topologies": ["squad-5", "constellation-10"],
        "surface_profiles": ["runtime-only", "observer-visualizer"],
    },
}


@dataclass(frozen=True)
class SisoRuntimeSurfaceMatrixPaths:
    output_dir: Path
    summary_json: Path
    results_csv: Path
    manifest_json: Path
    report_markdown: Path
    index_html: Path
    rows_root: Path


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return repr(value)


def _profile_map() -> dict[str, dict[str, Any]]:
    return {str(row["surface_profile"]): dict(row) for row in SURFACE_PROFILES}


def _merge_unique(primary: Sequence[str] | None, secondary: Sequence[str] | None) -> list[str] | None:
    ordered: list[str] = []
    for source in (primary or (), secondary or ()):
        for item in source:
            if item not in ordered:
                ordered.append(str(item))
    return ordered or None


def _select_showcase_rows(
    manifest: Mapping[str, Any],
    *,
    families: Sequence[str] | None = None,
    editions: Sequence[str] | None = None,
    topologies: Sequence[str] | None = None,
    scenarios: Sequence[str] | None = None,
) -> list[dict[str, Any]]:
    family_set = set(families or ())
    edition_set = set(editions or ())
    topology_set = set(topologies or ())
    scenario_set = set(scenarios or ())
    selected: list[dict[str, Any]] = []
    for row in manifest["scenarios"]:
        if family_set and str(row["family"]) not in family_set:
            continue
        if edition_set and str(row["runtime_edition"]) not in edition_set:
            continue
        if topology_set and str(row["topology"]) not in topology_set:
            continue
        if scenario_set and str(row["scenario"]) not in scenario_set:
            continue
        selected.append(dict(row))
    return selected


def build_siso_runtime_surface_matrix_manifest(
    *,
    manifest_path: str | Path | None = None,
    families: Sequence[str] | None = None,
    editions: Sequence[str] | None = None,
    topologies: Sequence[str] | None = None,
    scenarios: Sequence[str] | None = None,
    surface_profiles: Sequence[str] | None = None,
    presets: Sequence[str] | None = None,
) -> dict[str, Any]:
    selected_presets = [SURFACE_MATRIX_PRESETS[name] for name in (presets or ())]
    families = _merge_unique(families, [item for preset in selected_presets for item in preset.get("families", [])])
    editions = _merge_unique(editions, [item for preset in selected_presets for item in preset.get("editions", [])])
    topologies = _merge_unique(topologies, [item for preset in selected_presets for item in preset.get("topologies", [])])
    surface_profiles = _merge_unique(
        surface_profiles,
        [item for preset in selected_presets for item in preset.get("surface_profiles", [])],
    )
    showcase_manifest = load_siso_runtime_showcase_manifest(manifest_path)
    selected_showcase_rows = _select_showcase_rows(
        showcase_manifest,
        families=families,
        editions=editions,
        topologies=topologies,
        scenarios=scenarios,
    )
    profiles = _profile_map()
    requested_profiles = [profiles[name] for name in (surface_profiles or profiles.keys())]
    rows: list[dict[str, Any]] = []
    for showcase_row in selected_showcase_rows:
        for profile in requested_profiles:
            rows.append(
                {
                    **showcase_row,
                    **profile,
                    "matrix_row_id": f"{showcase_row['scenario']}::{profile['surface_profile']}",
                }
            )
    return {
        "schema_version": "siso-runtime-surface-matrix-v0.1",
        "showcase_manifest_path": str(manifest_path) if manifest_path is not None else None,
        "presets": list(presets or ()),
        "surface_profiles": [str(profile["surface_profile"]) for profile in requested_profiles],
        "scenario_count": len(selected_showcase_rows),
        "row_count": len(rows),
        "rows": rows,
    }


def _fetch_json(url: str, *, method: str = "GET", payload: Mapping[str, Any] | None = None) -> Any:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = request.Request(url, data=data, headers=headers, method=method)
    with request.urlopen(req, timeout=15.0) as response:
        return json.loads(response.read().decode("utf-8"))


def _wait_for_observer_state(base_url: str, *, timeout_seconds: float = 20.0) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    last_state: dict[str, Any] | None = None
    while time.time() < deadline:
        state = _fetch_json(f"{base_url}/api/state")
        last_state = dict(state)
        status = str(state.get("status", ""))
        summary_ready = bool(state.get("summary_ready"))
        history_count = int(state.get("history_event_count", 0))
        if summary_ready or history_count > 0 or status in {"completed", "failed", "stopped"}:
            return last_state
        time.sleep(0.2)
    if last_state is None:
        raise RuntimeError(f"Timed out waiting for observer state from {base_url!r}.")
    return last_state


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _client_json(client: TestClient, path: str, *, method: str = "GET", payload: Mapping[str, Any] | None = None) -> Any:
    response = client.request(method, path, json=payload)
    response.raise_for_status()
    return response.json()


def _wait_for_observer_client_state(client: TestClient, *, timeout_seconds: float = 20.0) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    last_state: dict[str, Any] | None = None
    while time.time() < deadline:
        state = _client_json(client, "/api/state")
        last_state = dict(state)
        status = str(state.get("status", ""))
        summary_ready = bool(state.get("summary_ready"))
        history_count = int(state.get("history_event_count", 0))
        if summary_ready or history_count > 0 or status in {"completed", "failed", "stopped"}:
            return last_state
        time.sleep(0.2)
    if last_state is None:
        raise RuntimeError("Timed out waiting for in-process observer state.")
    return last_state


def _normalize_observer_state_payload(state: Mapping[str, Any], events_payload: Any) -> dict[str, Any]:
    normalized = dict(state)
    events = events_payload.get("events", []) if isinstance(events_payload, Mapping) else []
    if "history_event_count" not in normalized:
        normalized["history_event_count"] = len(events)
    return normalized


def _capture_row_screenshots(
    page: Any,
    row_dir: Path,
    *,
    observer_url: str | None,
    federate_service_url: str | None,
) -> dict[str, Any]:
    gallery_dir = row_dir / "gallery"
    gallery_dir.mkdir(parents=True, exist_ok=True)
    captures: list[dict[str, str]] = []
    if observer_url:
        captures.extend(capture_live_visualizer(page, gallery_dir, base_url=observer_url, prefix="observer"))
    if federate_service_url:
        captures.extend(capture_live_federate_service(page, gallery_dir, base_url=federate_service_url, prefix="bridge"))
    index_path = write_gallery_index(gallery_dir, browser_name="shared-browser", captures=captures)
    manifest_path = write_gallery_manifest(
        gallery_dir,
        browser_name="shared-browser",
        captures=captures,
        index_path=index_path,
    )
    return {
        "status": "captured",
        "capture_count": len(captures),
        "gallery_index_html": str(index_path),
        "gallery_manifest_json": str(manifest_path),
    }


def _run_runtime_only_row(row: Mapping[str, Any], row_dir: Path) -> dict[str, Any]:
    result = run_siso_runtime_showcase_scenario(
        str(row["scenario"]),
        backend=str(row["python_backend"]),
        listener_output_dir=row_dir / "listener",
    )
    summary_path = row_dir / "listener" / str(row["scenario"]) / "listener_summary.json"
    return {
        "scenario_status": result["status"],
        "execution_complete": bool(result["execution_complete"]),
        "listener_event_count": int(result.get("listener_event_count", 0)),
        "observer_api_status": "not-included",
        "visualizer_status": "not-included",
        "bridge_api_status": "not-included",
        "listener_summary_json": str(summary_path),
        "scenario_result": result,
    }


def _run_observer_row(
    row: Mapping[str, Any],
    row_dir: Path,
    *,
    include_screenshots: bool,
    shared_page: Any | None,
) -> dict[str, Any]:
    observer_out = row_dir / "observer_runtime"
    app = build_runtime_observer_fastapi_app(
        output_dir=observer_out,
        backend=str(row["python_backend"]),
        provider="siso-runtime",
        scenario=str(row["scenario"]),
    )
    api_dir = row_dir / "api"
    api_dir.mkdir(parents=True, exist_ok=True)
    bridge_status = "not-included"
    bridge_contract_path: str | None = None
    screenshot_summary: dict[str, Any] = {"status": "not-requested"}
    if include_screenshots and shared_page is not None:
        with run_local_app(app) as observer_url:
            state = _wait_for_observer_state(observer_url)
            events_payload = _fetch_json(f"{observer_url}/api/events")
            state = _normalize_observer_state_payload(state, events_payload)
            _write_json(api_dir / "health.json", _fetch_json(f"{observer_url}/api/health"))
            _write_json(api_dir / "catalog.json", _fetch_json(f"{observer_url}/api/catalog"))
            _write_json(api_dir / "schema.json", _fetch_json(f"{observer_url}/api/schema"))
            _write_json(api_dir / "state.json", state)
            _write_json(api_dir / "events.json", events_payload)
            _write_json(api_dir / "objects.json", _fetch_json(f"{observer_url}/api/inspectors/objects"))
            _write_json(api_dir / "interactions.json", _fetch_json(f"{observer_url}/api/inspectors/interactions"))
            federate_service_url: str | None = None
            if bool(row["includes_federate_service_api"]):
                bridge_app = create_federate_service_fastapi_app()
                with run_local_app(bridge_app) as federate_service_url:
                    bridge_contract_path = str(
                        _write_json(
                            api_dir / "federate_service_contract.json",
                            _fetch_json(f"{federate_service_url}/api/contract"),
                        )
                    )
                    bridge_status = "captured"
                    screenshot_summary = _capture_row_screenshots(
                        shared_page,
                        row_dir,
                        observer_url=observer_url if bool(row["includes_visualizer_html"]) else None,
                        federate_service_url=federate_service_url,
                    )
            elif bool(row["includes_visualizer_html"]):
                screenshot_summary = _capture_row_screenshots(
                    shared_page,
                    row_dir,
                    observer_url=observer_url,
                    federate_service_url=None,
                )
            _fetch_json(f"{observer_url}/api/control/stop", method="POST", payload={})
    else:
        with TestClient(app) as observer_client:
            state = _wait_for_observer_client_state(observer_client)
            events_payload = _client_json(observer_client, "/api/events")
            state = _normalize_observer_state_payload(state, events_payload)
            _write_json(api_dir / "health.json", _client_json(observer_client, "/api/health"))
            _write_json(api_dir / "catalog.json", _client_json(observer_client, "/api/catalog"))
            _write_json(api_dir / "schema.json", _client_json(observer_client, "/api/schema"))
            _write_json(api_dir / "state.json", state)
            _write_json(api_dir / "events.json", events_payload)
            _write_json(api_dir / "objects.json", _client_json(observer_client, "/api/inspectors/objects"))
            _write_json(api_dir / "interactions.json", _client_json(observer_client, "/api/inspectors/interactions"))
            if bool(row["includes_federate_service_api"]):
                bridge_app = create_federate_service_fastapi_app()
                with TestClient(bridge_app) as bridge_client:
                    bridge_contract_path = str(
                        _write_json(
                            api_dir / "federate_service_contract.json",
                            _client_json(bridge_client, "/api/contract"),
                        )
                    )
                    bridge_status = "captured"
            _client_json(observer_client, "/api/control/stop", method="POST", payload={})
    state_path = api_dir / "state.json"
    state_payload = json.loads(state_path.read_text(encoding="utf-8"))
    listener_dir = observer_out / "listener" / str(row["scenario"])
    return {
        "scenario_status": str(state_payload.get("status", "unknown")),
        "execution_complete": bool(state_payload.get("summary_ready") or state_payload.get("history_event_count", 0)),
        "listener_event_count": int(state_payload.get("history_event_count", 0)),
        "observer_api_status": "captured",
        "visualizer_status": "captured" if bool(row["includes_visualizer_html"]) else "not-included",
        "bridge_api_status": bridge_status,
        "observer_state_json": str(state_path),
        "observer_schema_json": str(api_dir / "schema.json"),
        "bridge_contract_json": bridge_contract_path,
        "listener_summary_json": str(listener_dir / "listener_summary.json"),
        "screenshot_status": screenshot_summary["status"],
        "screenshot_summary": screenshot_summary,
    }


def _write_results_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> Path:
    fieldnames = [
        "matrix_row_id",
        "scenario",
        "family",
        "runtime_edition",
        "topology",
        "federate_count",
        "surface_profile",
        "includes_observer_api",
        "includes_visualizer_html",
        "includes_federate_service_api",
        "scenario_status",
        "execution_complete",
        "listener_event_count",
        "observer_api_status",
        "visualizer_status",
        "bridge_api_status",
        "screenshot_status",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: _jsonable(row.get(name, "")) for name in fieldnames})
    return path


def _write_index_html(path: Path, rows: Sequence[Mapping[str, Any]], summary: Mapping[str, Any]) -> Path:
    cards = []
    for row in rows:
        screenshot_summary = row.get("screenshot_summary") or {}
        detail_lines = [
            f"<li><strong>Scenario</strong>: <code>{html.escape(str(row['scenario']))}</code></li>",
            f"<li><strong>Family</strong>: <code>{html.escape(str(row['family']))}</code></li>",
            f"<li><strong>Edition</strong>: <code>{html.escape(str(row['runtime_edition']))}</code></li>",
            f"<li><strong>Topology</strong>: <code>{html.escape(str(row['topology']))}</code></li>",
            f"<li><strong>Surface</strong>: <code>{html.escape(str(row['surface_profile']))}</code></li>",
            f"<li><strong>Observer API</strong>: <code>{html.escape(str(row['observer_api_status']))}</code></li>",
            f"<li><strong>Visualizer</strong>: <code>{html.escape(str(row['visualizer_status']))}</code></li>",
            f"<li><strong>Bridge API</strong>: <code>{html.escape(str(row['bridge_api_status']))}</code></li>",
            f"<li><strong>Screenshots</strong>: <code>{html.escape(str(row.get('screenshot_status', 'n/a')))}</code></li>",
        ]
        link_items = []
        for label, key in (
            ("Observer state", "observer_state_json"),
            ("Observer schema", "observer_schema_json"),
            ("Bridge contract", "bridge_contract_json"),
            ("Listener summary", "listener_summary_json"),
        ):
            value = row.get(key)
            if value:
                link_items.append(
                    f'<a href="{html.escape(Path(str(value)).resolve().as_uri())}">{html.escape(label)}</a>'
                )
        gallery_index = screenshot_summary.get("gallery_index_html")
        if gallery_index:
            link_items.append(
                f'<a href="{html.escape(Path(str(gallery_index)).resolve().as_uri())}">Screenshot gallery</a>'
            )
        cards.append(
            f"""
            <article class="card">
              <h2>{html.escape(str(row['scenario']))}</h2>
              <p class="story">{html.escape(str(row.get('story', '')))}</p>
              <ul>{''.join(detail_lines)}</ul>
              <div class="links">{' | '.join(link_items) if link_items else '<span>no linked artifacts</span>'}</div>
            </article>
            """
        )
    body = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SISO Runtime Surface Matrix</title>
  <style>
    body {{ margin: 0; font: 15px/1.55 "Avenir Next", "Segoe UI", sans-serif; color: #1d2a35; background: linear-gradient(180deg, #f2ebdf, #e7dece); }}
    main {{ max-width: 1500px; margin: 0 auto; padding: 24px; }}
    .hero {{ background: rgba(255,255,255,0.84); border: 1px solid rgba(0,0,0,0.08); border-radius: 18px; padding: 20px; margin-bottom: 20px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 18px; }}
    .card {{ background: rgba(255,255,255,0.9); border: 1px solid rgba(0,0,0,0.08); border-radius: 18px; padding: 16px; }}
    h1, h2 {{ margin-top: 0; }}
    ul {{ padding-left: 18px; }}
    code {{ background: rgba(0,0,0,0.05); padding: 2px 6px; border-radius: 6px; }}
    .story {{ color: #596876; }}
    .links {{ margin-top: 12px; word-break: break-word; }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <h1>SISO Runtime Surface Matrix</h1>
      <p>Scenario-aware observer, visualizer, bridge, and screenshot artifact index.</p>
      <p>Rows: <code>{html.escape(str(summary['selected_row_count']))}</code> | Scenarios: <code>{html.escape(str(summary['selected_scenario_count']))}</code> | Screenshot runtime: <code>{html.escape(str(summary['screenshot_runtime_status']))}</code></p>
    </section>
    <section class="grid">
      {''.join(cards)}
    </section>
  </main>
</body>
</html>
"""
    path.write_text(body, encoding="utf-8")
    return path


def _render_markdown(summary: Mapping[str, Any], paths: SisoRuntimeSurfaceMatrixPaths) -> str:
    lines = [
        "# SISO Runtime Surface Matrix",
        "",
        f"- suite: `{summary['suite_name']}`",
        f"- status: `{summary['status']}`",
        f"- selected scenarios: `{summary['selected_scenario_count']}`",
        f"- selected rows: `{summary['selected_row_count']}`",
        f"- screenshots requested: `{summary['include_screenshots']}`",
        f"- screenshot runtime: `{summary['screenshot_runtime_status']}`",
        f"- summary json: `{paths.summary_json}`",
        f"- results csv: `{paths.results_csv}`",
        f"- manifest json: `{paths.manifest_json}`",
        f"- index html: `{paths.index_html}`",
        "",
        "## Matrix",
        "",
        "| Scenario | Edition | Family | Topology | Surface Profile | Observer API | Visualizer | Bridge API | Screenshots |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in summary["results"]:
        lines.append(
            "| "
            + " | ".join(
                (
                    str(row["scenario"]),
                    str(row["runtime_edition"]),
                    str(row["family"]),
                    str(row["topology"]),
                    str(row["surface_profile"]),
                    str(row["observer_api_status"]),
                    str(row["visualizer_status"]),
                    str(row["bridge_api_status"]),
                    str(row.get("screenshot_status", "n/a")),
                )
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def write_siso_runtime_surface_matrix_artifacts(
    output_dir: str | Path,
    *,
    manifest_path: str | Path | None = None,
    families: Sequence[str] | None = None,
    editions: Sequence[str] | None = None,
    topologies: Sequence[str] | None = None,
    scenarios: Sequence[str] | None = None,
    surface_profiles: Sequence[str] | None = None,
    presets: Sequence[str] | None = None,
    include_screenshots: bool = False,
    fail_on_screenshot_errors: bool = False,
) -> SisoRuntimeSurfaceMatrixPaths:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = SisoRuntimeSurfaceMatrixPaths(
        output_dir=out,
        summary_json=out / "siso_runtime_surface_matrix_summary.json",
        results_csv=out / "siso_runtime_surface_matrix_results.csv",
        manifest_json=out / "siso_runtime_surface_matrix_manifest.json",
        report_markdown=out / "siso_runtime_surface_matrix_report.md",
        index_html=out / "siso_runtime_surface_matrix_index.html",
        rows_root=out / "rows",
    )
    manifest = build_siso_runtime_surface_matrix_manifest(
        manifest_path=manifest_path,
        families=families,
        editions=editions,
        topologies=topologies,
        scenarios=scenarios,
        surface_profiles=surface_profiles,
        presets=presets,
    )
    page = None
    pw = None
    browser = None
    screenshot_runtime_status = "not-requested"
    if include_screenshots:
        try:
            pw, browser, browser_name = launch_browser()
            page = browser.new_page()
            screenshot_runtime_status = f"ready:{browser_name}"
        except BaseException as exc:
            screenshot_runtime_status = f"unavailable:{exc}"
            if fail_on_screenshot_errors:
                raise
    try:
        results: list[dict[str, Any]] = []
        for row in manifest["rows"]:
            row_dir = paths.rows_root / str(row["scenario"]) / str(row["surface_profile"])
            row_dir.mkdir(parents=True, exist_ok=True)
            if str(row["surface_profile"]) == "runtime-only":
                row_result = _run_runtime_only_row(row, row_dir)
                row_result["screenshot_status"] = "not-applicable"
            else:
                row_result = _run_observer_row(
                    row,
                    row_dir,
                    include_screenshots=include_screenshots and page is not None,
                    shared_page=page,
                )
                if include_screenshots and page is None and row_result.get("screenshot_status") == "not-requested":
                    row_result["screenshot_status"] = screenshot_runtime_status
            results.append({**row, **row_result})
    finally:
        if browser is not None:
            browser.close()
        if pw is not None:
            pw.stop()
    summary = {
        "suite_name": "siso-runtime-surface-matrix",
        "status": "green" if all(bool(row.get("execution_complete")) for row in results) else "failed",
        "selected_scenario_count": int(manifest["scenario_count"]),
        "selected_row_count": int(manifest["row_count"]),
        "include_screenshots": include_screenshots,
        "screenshot_runtime_status": screenshot_runtime_status,
        "results": results,
        "manifest": manifest,
    }
    _write_json(paths.summary_json, summary)
    _write_json(paths.manifest_json, manifest)
    _write_results_csv(paths.results_csv, results)
    _write_index_html(paths.index_html, results, summary)
    paths.report_markdown.write_text(_render_markdown(summary, paths), encoding="utf-8")
    return paths


__all__ = [
    "SURFACE_MATRIX_PRESETS",
    "SisoRuntimeSurfaceMatrixPaths",
    "build_siso_runtime_surface_matrix_manifest",
    "write_siso_runtime_surface_matrix_artifacts",
]
