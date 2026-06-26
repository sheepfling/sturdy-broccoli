"""Local HTTP/SSE observer and control plane for runtime showcase lanes."""
from __future__ import annotations

import json
import multiprocessing
import threading
import time
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import parse_qs, urlparse

from .runtime_event_stream import RuntimeEventStreamWriter
from .siso_runtime_showcase import build_siso_runtime_showcase_manifest, run_siso_runtime_showcase_scenario
from .target_radar_proof import write_target_radar_proof_artifacts
from .workspace_two_federate_suite import write_workspace_two_federate_suite_artifacts

RUNTIME_OBSERVER_EVENT_SCHEMA_VERSION = "runtime-observer-event-schema-v1"


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


def _load_ndjson(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _events_after(events: list[dict[str, Any]], after_sequence: int) -> list[dict[str, Any]]:
    return [event for event in events if int(event.get("sequence", 0)) > after_sequence]


def _text_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _family_from_class_name(class_name: Any) -> str:
    text = (_text_or_none(class_name) or "").lower()
    if not text:
        return "generic"
    if "link16" in text or "jtids" in text or "rttab" in text or "radiotransmitter" in text:
        return "link16"
    if "rpr" in text or "baseentity" in text or "munition" in text or "weaponfire" in text:
        return "rpr"
    if "space" in text or "satellite" in text or "orbital" in text:
        return "space"
    if "track" in text or "radar" in text or "target" in text:
        return "target-radar"
    return "generic"


def _event_class_name(event: Mapping[str, Any]) -> str | None:
    for key in ("class_name", "interaction_class"):
        value = _text_or_none(event.get(key))
        if value:
            return value
    return None


def _event_family(event: Mapping[str, Any]) -> str:
    explicit = _text_or_none(event.get("family"))
    if explicit:
        return explicit
    return _family_from_class_name(_event_class_name(event))


def _object_identity_key(event: Mapping[str, Any]) -> str:
    for key in ("object_key", "object_handle_text", "entity_handle_text", "object_name", "entity_name"):
        value = _text_or_none(event.get(key))
        if value:
            return value
    class_name = _text_or_none(event.get("class_name")) or "object"
    return f"{class_name}::anonymous"


def _interaction_identity_key(event: Mapping[str, Any], *, index: int) -> str:
    for key in ("interaction_key", "class_handle_text", "interaction_class"):
        value = _text_or_none(event.get(key))
        if value:
            return f"{value}::{index}"
    return f"interaction::{index}"


def build_runtime_observer_event_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://example.invalid/runtime-observer-event-schema.json",
        "title": "Runtime Observer Normalized Event Schema",
        "description": "Stable normalized event and inspector payloads exposed by the federation subscriber.",
        "schema_version": RUNTIME_OBSERVER_EVENT_SCHEMA_VERSION,
        "event_types": [
            "scenario.phase",
            "scenario.operation",
            "object.discovered",
            "object.updated",
            "interaction.received",
            "event.raw",
        ],
        "family_values": [
            "generic",
            "link16",
            "rpr",
            "space",
            "target-radar",
        ],
        "normalized_event_required": [
            "event_type",
            "provider",
            "scenario",
            "family",
            "sequence",
        ],
        "normalized_event_properties": {
            "sequence": "Integer source event sequence from the observer trace.",
            "event_type": "Stable normalized category for subscriber clients.",
            "provider": "Scenario provider lane such as siso-runtime, two-federate, or target-radar.",
            "scenario": "Scenario identifier.",
            "family": "Derived or declared FOM family classification.",
            "source": "Listener or emitting federate identity when available.",
            "observer_role": "Role of the observing federate when available.",
            "phase": "Scenario phase label for scenario.phase events.",
            "operation": "Operation label for scenario.operation events.",
            "target": "Operation target for scenario.operation events.",
            "details": "Scenario phase or operation detail payload.",
            "object_key": "Stable object identity key used by the generic object inspector.",
            "object_name": "Human-readable object instance name when available.",
            "object_handle_text": "Text form of the RTI object-instance handle when available.",
            "class_name": "Resolved object or interaction class name when available.",
            "class_handle_text": "Text form of the RTI class handle when available.",
            "attributes": "Reflected attribute map for object.updated events.",
            "interaction_class": "Resolved interaction class name for interaction.received events.",
            "interaction_key": "Stable interaction row identity key.",
            "parameters": "Interaction parameter map for interaction.received events.",
            "tag": "User-supplied tag or equivalent correlation bytes converted to text/hex.",
            "payload": "Original raw payload when no stronger normalized field exists.",
        },
        "object_inspector_fields": [
            "object_key",
            "object_id",
            "object_name",
            "object_handle_text",
            "class_name",
            "class_handle_text",
            "family",
            "attributes",
            "discovery_count",
            "update_count",
            "last_tag",
            "sources",
            "aliases",
        ],
        "interaction_inspector_fields": [
            "interaction_key",
            "interaction_class",
            "class_handle_text",
            "family",
            "source",
            "observer_role",
            "tag",
            "parameters",
        ],
    }


def _derive_live_metrics(events: list[dict[str, Any]]) -> dict[str, Any]:
    phases: list[str] = []
    operations = 0
    callbacks = {
        "discoverObjectInstance": 0,
        "reflectAttributeValues": 0,
        "receiveInteraction": 0,
    }
    for event in events:
        if event.get("kind") == "phase":
            phases.append(str(event.get("phase", "")))
        elif event.get("kind") == "operation":
            operations += 1
        elif event.get("kind") == "callback":
            callback = str(event.get("callback", ""))
            if callback in callbacks:
                callbacks[callback] += 1
    return {
        "event_count": len(events),
        "phases": phases,
        "last_phase": phases[-1] if phases else None,
        "operations": operations,
        "callbacks": callbacks,
        "last_event": events[-1] if events else None,
    }


def _normalize_event(event: Mapping[str, Any]) -> dict[str, Any]:
    kind = str(event.get("kind", ""))
    sequence = int(event.get("sequence", 0))
    provider = event.get("provider")
    scenario = event.get("scenario")
    source = event.get("listener_name") or event.get("actor")
    observer_role = event.get("listener_role")
    if kind == "phase":
        return {
            "sequence": sequence,
            "event_type": "scenario.phase",
            "provider": provider,
            "scenario": scenario,
            "family": _event_family(event),
            "source": source,
            "observer_role": observer_role,
            "phase": event.get("phase"),
            "details": event.get("details", {}),
        }
    if kind == "operation":
        return {
            "sequence": sequence,
            "event_type": "scenario.operation",
            "provider": provider,
            "scenario": scenario,
            "family": _event_family(event),
            "source": source,
            "observer_role": observer_role,
            "operation": event.get("operation"),
            "actor": event.get("actor"),
            "target": event.get("target"),
            "tag": event.get("tag"),
            "details": event.get("details", {}),
        }
    callback = str(event.get("callback") or event.get("event") or "")
    if callback == "discoverObjectInstance":
        class_name = _text_or_none(event.get("class_name"))
        object_name = _text_or_none(event.get("entity_name"))
        object_handle_text = _text_or_none(event.get("entity_handle_text"))
        return {
            "sequence": sequence,
            "event_type": "object.discovered",
            "provider": provider,
            "scenario": scenario,
            "family": _event_family(event),
            "object_key": object_handle_text or object_name or class_name or "object",
            "object_name": object_name,
            "object_handle_text": object_handle_text,
            "class_name": class_name,
            "class_handle_text": _text_or_none(event.get("class_handle_text")),
            "source": source,
            "observer_role": observer_role,
            "payload": event.get("payload"),
        }
    if callback == "reflectAttributeValues":
        class_name = _text_or_none(event.get("class_name"))
        object_name = _text_or_none(event.get("entity_name"))
        object_handle_text = _text_or_none(event.get("entity_handle_text"))
        return {
            "sequence": sequence,
            "event_type": "object.updated",
            "provider": provider,
            "scenario": scenario,
            "family": _event_family(event),
            "object_key": object_handle_text or object_name or class_name or "object",
            "object_name": object_name,
            "object_handle_text": object_handle_text,
            "class_name": class_name,
            "class_handle_text": _text_or_none(event.get("class_handle_text")),
            "source": source,
            "observer_role": observer_role,
            "attributes": event.get("values") if isinstance(event.get("values"), Mapping) else event.get("payload"),
            "tag": event.get("tag"),
        }
    if callback in {"receiveInteraction", "track", "query_rcs"}:
        interaction_class = _text_or_none(event.get("class_name")) or _text_or_none(event.get("event")) or callback
        return {
            "sequence": sequence,
            "event_type": "interaction.received",
            "provider": provider,
            "scenario": scenario,
            "family": _event_family({"class_name": interaction_class}),
            "interaction_key": f"{interaction_class}::{sequence}",
            "interaction_class": interaction_class,
            "class_handle_text": _text_or_none(event.get("class_handle_text")),
            "source": source,
            "observer_role": observer_role,
            "parameters": event.get("values") if isinstance(event.get("values"), Mapping) else event.get("payload"),
            "tag": event.get("tag"),
        }
    return {
        "sequence": sequence,
        "event_type": "event.raw",
        "provider": provider,
        "scenario": scenario,
        "family": _event_family(event),
        "source": source,
        "observer_role": observer_role,
        "raw_kind": kind,
        "payload": dict(event),
    }


def _derive_generic_inspectors(state: Mapping[str, Any], normalized_events: list[dict[str, Any]]) -> dict[str, Any]:
    objects: dict[str, dict[str, Any]] = {}
    interactions: list[dict[str, Any]] = []

    def ensure_object(
        key: str,
        *,
        object_name: str | None = None,
        object_handle_text: str | None = None,
        class_name: str | None = None,
        class_handle_text: str | None = None,
        family: str | None = None,
    ) -> dict[str, Any]:
        entry = objects.setdefault(
            key,
            {
                "object_key": key,
                "object_id": key,
                "object_name": object_name or key,
                "object_handle_text": object_handle_text,
                "class_name": class_name or "",
                "class_handle_text": class_handle_text,
                "family": family or _family_from_class_name(class_name),
                "attributes": {},
                "update_count": 0,
                "discovery_count": 0,
                "last_tag": None,
                "sources": [],
                "aliases": [],
            },
        )
        if object_name and entry["object_name"] in {"", key}:
            entry["object_name"] = object_name
        if object_handle_text and not entry["object_handle_text"]:
            entry["object_handle_text"] = object_handle_text
        if class_name and not entry["class_name"]:
            entry["class_name"] = class_name
        if class_handle_text and not entry["class_handle_text"]:
            entry["class_handle_text"] = class_handle_text
        if family and entry["family"] == "generic":
            entry["family"] = family
        if object_name and object_name not in entry["aliases"]:
            entry["aliases"].append(object_name)
        return entry

    for index, event in enumerate(normalized_events, start=1):
        event_type = str(event.get("event_type", ""))
        if event_type == "object.discovered":
            object_name = _text_or_none(event.get("object_name"))
            key = _object_identity_key(event)
            entry = ensure_object(
                key,
                object_name=object_name,
                object_handle_text=_text_or_none(event.get("object_handle_text")),
                class_name=_text_or_none(event.get("class_name")),
                class_handle_text=_text_or_none(event.get("class_handle_text")),
                family=_text_or_none(event.get("family")),
            )
            entry["discovery_count"] += 1
            source = _text_or_none(event.get("source"))
            if source and source not in entry["sources"]:
                entry["sources"].append(source)
        elif event_type == "object.updated":
            object_name = _text_or_none(event.get("object_name"))
            key = _object_identity_key(event)
            entry = ensure_object(
                key,
                object_name=object_name,
                object_handle_text=_text_or_none(event.get("object_handle_text")),
                class_name=_text_or_none(event.get("class_name")),
                class_handle_text=_text_or_none(event.get("class_handle_text")),
                family=_text_or_none(event.get("family")),
            )
            entry["update_count"] += 1
            values = event.get("attributes")
            if isinstance(values, Mapping):
                entry["attributes"].update(values)
            if event.get("tag") is not None:
                entry["last_tag"] = event.get("tag")
            source = _text_or_none(event.get("source"))
            if source and source not in entry["sources"]:
                entry["sources"].append(source)
        elif event_type == "interaction.received":
            interactions.append(
                {
                    "interaction_key": _interaction_identity_key(event, index=index),
                    "interaction_class": str(event.get("interaction_class") or ""),
                    "class_handle_text": _text_or_none(event.get("class_handle_text")),
                    "family": _text_or_none(event.get("family")) or _family_from_class_name(event.get("interaction_class")),
                    "source": str(event.get("source") or ""),
                    "observer_role": _text_or_none(event.get("observer_role")),
                    "tag": event.get("tag"),
                    "parameters": event.get("parameters"),
                }
            )

    final_summary = state.get("final_summary")
    if isinstance(final_summary, Mapping):
        proof = final_summary.get("proof")
        if isinstance(proof, Mapping):
            for report in proof.get("track_reports", []):
                if isinstance(report, Mapping):
                    interactions.append(
                        {
                            "interaction_class": "TrackReport",
                            "source": "target-radar-plugin",
                            "tag": None,
                            "parameters": dict(report),
                        }
                    )

    return {
        "objects": sorted(
            objects.values(),
            key=lambda item: (
                str(item.get("family", "")),
                str(item.get("class_name", "")),
                str(item.get("object_name", "")),
                str(item.get("object_handle_text", "")),
            ),
        ),
        "interactions": interactions,
    }


def _derive_target_radar_plugin(state: Mapping[str, Any], events: list[dict[str, Any]]) -> dict[str, Any] | None:
    provider = str(state.get("provider", ""))
    scenario = str(state.get("scenario", ""))
    if provider != "target-radar" and scenario != "target_radar":
        return None
    track_reports: list[dict[str, Any]] = []
    for event in events:
        if str(event.get("interaction_class", "")) == "track" and isinstance(event.get("parameters"), Mapping):
            track_reports.append(dict(event["parameters"]))
    final_summary = state.get("final_summary")
    if isinstance(final_summary, Mapping):
        proof = final_summary.get("proof")
        if isinstance(proof, Mapping):
            for report in proof.get("track_reports", []):
                if isinstance(report, Mapping):
                    track_reports.append(dict(report))
    deduped: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for row in track_reports:
        track_id = str(row.get("track_id", len(deduped)))
        if track_id in seen_ids:
            continue
        seen_ids.add(track_id)
        deduped.append(row)
    return {
        "plugin_id": "target-radar",
        "title": "Target/Radar Panel",
        "track_reports": deduped,
        "track_report_count": len(deduped),
        "latest_track": deduped[-1] if deduped else None,
    }


def _derive_rpr_plugin(state: Mapping[str, Any], inspectors: Mapping[str, Any]) -> dict[str, Any] | None:
    if str(state.get("family", "")) != "rpr" and str(state.get("scenario", "")) not in {"workspace-two-federate"}:
        return None
    interactions = [row for row in inspectors.get("interactions", []) if isinstance(row, Mapping)]
    fire_rows = [row for row in interactions if "WeaponFire" in str(row.get("interaction_class", ""))]
    detonation_rows = [row for row in interactions if "MunitionDetonation" in str(row.get("interaction_class", ""))]
    bridge_rows = [row for row in inspectors.get("objects", []) if "Bridge" in str(row.get("class_name", "")) or "Bridge" in str(row.get("object_name", ""))]
    return {
        "plugin_id": "rpr",
        "title": "RPR Engagement Panel",
        "bridge_objects": bridge_rows,
        "weapon_fire_count": len(fire_rows),
        "detonation_count": len(detonation_rows),
        "recent_weapon_fire": fire_rows[-3:],
        "recent_detonations": detonation_rows[-3:],
    }


def _derive_link16_plugin(state: Mapping[str, Any], inspectors: Mapping[str, Any]) -> dict[str, Any] | None:
    if str(state.get("family", "")) != "link16":
        return None
    objects = [row for row in inspectors.get("objects", []) if "RadioTransmitter" in str(row.get("class_name", ""))]
    interactions = [row for row in inspectors.get("interactions", []) if isinstance(row, Mapping)]
    jtids_rows = [row for row in interactions if "JTIDS" in str(row.get("interaction_class", ""))]
    rttab_rows = [row for row in interactions if "RTTAB" in str(row.get("interaction_class", ""))]
    return {
        "plugin_id": "link16",
        "title": "Link 16 Traffic Panel",
        "radio_objects": objects,
        "jtids_count": len(jtids_rows),
        "rttab_count": len(rttab_rows),
        "recent_jtids": jtids_rows[-3:],
        "recent_rttab": rttab_rows[-3:],
    }


def build_runtime_observer_catalog() -> dict[str, Any]:
    manifest = build_siso_runtime_showcase_manifest()
    return {
        "providers": [
            {
                "provider": "siso-runtime",
                "label": "SISO Runtime Showcase",
                "supports_live_callbacks": True,
                "scenarios": [
                    {
                        "id": row["scenario"],
                        "label": f"{row['family']} {row['runtime_edition']} {row['topology']}",
                        "family": row["family"],
                        "runtime_edition": row["runtime_edition"],
                        "topology": row["topology"],
                        "story": row["story"],
                        "participant_profiles": row.get("participant_profiles", []),
                        "plugin_panels": ["link16"] if row["family"] == "link16" else ["rpr"] if row["family"] == "rpr" else [],
                    }
                    for row in manifest["scenarios"]
                ],
            },
            {
                "provider": "two-federate",
                "label": "Workspace Two-Federate Suite",
                "supports_live_callbacks": False,
                "scenarios": [
                    {
                        "id": "workspace-two-federate",
                        "label": "Workspace Two-Federate Suite",
                        "story": "Composite two-federate suite with exchange, sync, ownership, save/restore, DDM, and Target/Radar time-window proofs.",
                        "default_options": {"target_radar_steps": 4},
                    }
                ],
            },
            {
                "provider": "target-radar",
                "label": "Target/Radar Proof",
                "supports_live_callbacks": False,
                "scenarios": [
                    {
                        "id": "target-radar-proof",
                        "label": "Target/Radar Proof",
                        "story": "Target/Radar truth, radar, and track-report proof lane with backend matrix artifacts.",
                        "default_options": {"target_radar_steps": 4},
                        "plugin_panels": ["target-radar"],
                    }
                ],
            },
        ]
    }


def _worker_main(provider: str, scenario: str, output_dir: str, backend: str | None, options: dict[str, Any]) -> None:
    out = Path(output_dir)
    trace_path = out / "runtime_observer_trace.ndjson"
    writer = RuntimeEventStreamWriter(trace_path)
    event_sink = writer.emit
    if provider == "siso-runtime":
        run_siso_runtime_showcase_scenario(
            scenario,
            backend=backend,
            listener_output_dir=out / "listener",
        )
        return
    if provider == "two-federate":
        event_sink({"kind": "phase", "provider": provider, "phase": "suite-start", "details": dict(options)})
        write_workspace_two_federate_suite_artifacts(
            out,
            target_radar_steps=int(options.get("target_radar_steps", 4)),
            event_sink=event_sink,
        )
        event_sink({"kind": "phase", "provider": provider, "phase": "suite-complete"})
        return
    if provider == "target-radar":
        event_sink({"kind": "phase", "provider": provider, "phase": "scenario-start", "details": dict(options)})
        write_target_radar_proof_artifacts(
            out,
            [backend or "python1516e"],
            proof_backend=backend or "python1516e",
            target_radar_steps=int(options.get("target_radar_steps", 4)),
            event_sink=event_sink,
        )
        event_sink({"kind": "phase", "provider": provider, "phase": "scenario-complete"})
        return
    raise KeyError(f"Unknown provider {provider!r}")


@dataclass(frozen=True)
class RuntimeObserverPaths:
    output_dir: Path
    scenario_dir: Path
    trace_ndjson: Path
    summary_json: Path
    report_html: Path


@dataclass(frozen=True)
class ObservedScenarioSpec:
    provider: str
    scenario: str
    label: str
    story: str
    supports_live_callbacks: bool
    participant_profiles: list[dict[str, Any]]
    metadata: dict[str, Any]


def _resolve_spec(provider: str, scenario: str) -> ObservedScenarioSpec:
    catalog = build_runtime_observer_catalog()
    for provider_row in catalog["providers"]:
        if provider_row["provider"] != provider:
            continue
        for row in provider_row["scenarios"]:
            if row["id"] != scenario:
                continue
            return ObservedScenarioSpec(
                provider=provider,
                scenario=scenario,
                label=str(row["label"]),
                story=str(row["story"]),
                supports_live_callbacks=bool(provider_row["supports_live_callbacks"]),
                participant_profiles=list(row.get("participant_profiles", [])),
                metadata=dict(row),
            )
    raise KeyError(f"Unknown provider/scenario {provider!r}/{scenario!r}")


class RuntimeObserverSession:
    def __init__(
        self,
        *,
        provider: str,
        scenario: str,
        output_dir: str | Path,
        backend: str | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> None:
        self.spec = _resolve_spec(provider, scenario)
        out = Path(output_dir)
        scenario_dir = out / "listener" / scenario if provider == "siso-runtime" else out
        if provider == "siso-runtime":
            summary_json = scenario_dir / "listener_summary.json"
            report_html = scenario_dir / "listener_report.html"
            trace_ndjson = scenario_dir / "listener_trace.ndjson"
        elif provider == "two-federate":
            summary_json = out / "two_federate_suite_summary.json"
            report_html = out / "two_federate_suite_report.md"
            trace_ndjson = out / "runtime_observer_trace.ndjson"
        else:
            summary_json = out / "target_radar_proof_summary.json"
            report_html = out / "target_radar_proof_report.md"
            trace_ndjson = out / "runtime_observer_trace.ndjson"
        self.paths = RuntimeObserverPaths(
            output_dir=out,
            scenario_dir=scenario_dir,
            trace_ndjson=trace_ndjson,
            summary_json=summary_json,
            report_html=report_html,
        )
        self.backend = backend
        self.options = dict(options or {})
        self._lock = threading.Lock()
        self._status = "created"
        self._error: str | None = None
        self._stopped = False
        ctx = multiprocessing.get_context("spawn")
        self._process = ctx.Process(
            target=_worker_main,
            args=(provider, scenario, str(out), backend, dict(self.options)),
            daemon=True,
        )

    def start(self) -> None:
        self.paths.scenario_dir.mkdir(parents=True, exist_ok=True)
        with self._lock:
            self._status = "running"
        self._process.start()

    def stop(self) -> None:
        with self._lock:
            self._stopped = True
            self._status = "stopped"
        if self._process.is_alive():
            self._process.terminate()
            self._process.join(timeout=2.0)

    def _refresh_status(self) -> None:
        if self._stopped:
            return
        if self._process.is_alive():
            return
        exitcode = self._process.exitcode
        with self._lock:
            if self._status in {"complete", "failed", "stopped"}:
                return
            if exitcode == 0:
                self._status = "complete"
            else:
                self._status = "failed"
                self._error = f"worker exit code {exitcode}"

    def _siso_events(self) -> list[dict[str, Any]]:
        return _load_ndjson(self.paths.trace_ndjson)

    def events(self, *, after_sequence: int = 0) -> list[dict[str, Any]]:
        self._refresh_status()
        events = _load_ndjson(self.paths.trace_ndjson)
        return _events_after(events, after_sequence)

    def live_state(self) -> dict[str, Any]:
        self._refresh_status()
        with self._lock:
            status = self._status
            error = self._error
        summary = _load_json(self.paths.summary_json)
        events = _load_ndjson(self.paths.trace_ndjson)
        metrics = _derive_live_metrics(events)
        normalized_events = [_normalize_event(event) for event in events]
        inspectors = _derive_generic_inspectors(
            {
                "provider": self.spec.provider,
                "scenario": self.spec.scenario,
                "final_summary": summary,
            },
            normalized_events,
        )
        plugin_panels = []
        target_radar_plugin = _derive_target_radar_plugin(
            {
                "provider": self.spec.provider,
                "scenario": self.spec.scenario,
                "final_summary": summary,
            },
            normalized_events,
        )
        if target_radar_plugin is not None:
            plugin_panels.append(target_radar_plugin)
        rpr_plugin = _derive_rpr_plugin(
            {
                "provider": self.spec.provider,
                "scenario": self.spec.scenario,
                "family": self.spec.metadata.get("family"),
            },
            inspectors,
        )
        if rpr_plugin is not None:
            plugin_panels.append(rpr_plugin)
        link16_plugin = _derive_link16_plugin(
            {
                "provider": self.spec.provider,
                "scenario": self.spec.scenario,
                "family": self.spec.metadata.get("family"),
            },
            inspectors,
        )
        if link16_plugin is not None:
            plugin_panels.append(link16_plugin)
        payload = {
            "provider": self.spec.provider,
            "scenario": self.spec.scenario,
            "label": self.spec.label,
            "story": self.spec.story,
            "supports_live_callbacks": self.spec.supports_live_callbacks,
            "participant_profiles": self.spec.participant_profiles,
            "backend": self.backend,
            "options": dict(self.options),
            "status": status,
            "error": error,
            "summary_ready": summary is not None,
            "listener_report_ready": self.paths.report_html.exists(),
            "artifacts": {
                "trace_ndjson": str(self.paths.trace_ndjson),
                "summary_json": str(self.paths.summary_json),
                "report_html": str(self.paths.report_html),
            },
            "live_metrics": metrics,
            "final_summary": summary,
            "catalog_metadata": self.spec.metadata,
            "inspectors": inspectors,
            "plugin_panels": plugin_panels,
            "normalized_events": normalized_events,
            "schema_version": RUNTIME_OBSERVER_EVENT_SCHEMA_VERSION,
        }
        if self.spec.provider == "siso-runtime":
            payload.update(
                {
                    "family": self.spec.metadata.get("family"),
                "runtime_edition": self.spec.metadata.get("runtime_edition"),
                    "topology": self.spec.metadata.get("topology"),
                    "federate_count": self.spec.metadata.get("federate_count"),
                    "source_packet": self.spec.metadata.get("source_packet"),
                    "fom_modules": self.spec.metadata.get("fom_modules", []),
                    "vendor_status": self.spec.metadata.get("vendor_status"),
                }
            )
        return payload


class RuntimeObserverControl:
    def __init__(self, *, output_dir: str | Path, default_backend: str | None = None) -> None:
        self.output_dir = Path(output_dir)
        self.default_backend = default_backend
        self._lock = threading.Lock()
        self._session: RuntimeObserverSession | None = None

    def catalog(self) -> dict[str, Any]:
        return build_runtime_observer_catalog()

    def current_session(self) -> RuntimeObserverSession | None:
        with self._lock:
            session = self._session
        return session

    def start(
        self,
        *,
        provider: str,
        scenario: str,
        backend: str | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> RuntimeObserverSession:
        with self._lock:
            if self._session is not None:
                current = self._session.live_state()
                if current["status"] == "running":
                    raise RuntimeError("A scenario is already running")
            session = RuntimeObserverSession(
                provider=provider,
                scenario=scenario,
                output_dir=self.output_dir / provider / scenario,
                backend=backend or self.default_backend,
                options={**dict(_resolve_spec(provider, scenario).metadata.get("default_options", {})), **dict(options or {})},
            )
            self._session = session
        session.start()
        return session

    def stop(self) -> dict[str, Any]:
        session = self.current_session()
        if session is None:
            return {"status": "idle"}
        session.stop()
        return session.live_state()

    def state(self) -> dict[str, Any]:
        session = self.current_session()
        if session is None:
            return {"status": "idle", "catalog": self.catalog()}
        return session.live_state()

    def events(self, *, after_sequence: int = 0) -> list[dict[str, Any]]:
        session = self.current_session()
        if session is None:
            return []
        return session.events(after_sequence=after_sequence)


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
  <title>Federation Subscriber</title>
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
      <h1>Federation Subscriber</h1>
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
      if (panel.plugin_id === "target-radar") {{
        const rows = (panel.track_reports || []).map((row) =>
          `<tr><td>${{row.track_id || ""}}</td><td>${{row.target_name || ""}}</td><td>${{row.range_m || ""}}</td><td>${{row.bearing_rad || ""}}</td><td>${{row.time_seconds || ""}}</td></tr>`
        ).join("");
        return `
          <div class="plugin-grid">
            <div class="plugin-card"><strong>Track Reports</strong><br>${{panel.track_report_count || 0}}</div>
            <div class="plugin-card"><strong>Latest Track</strong><br>${{(panel.latest_track && panel.latest_track.track_id) || "n/a"}}</div>
            <div class="plugin-card"><strong>Latest Target</strong><br>${{(panel.latest_track && panel.latest_track.target_name) || "n/a"}}</div>
          </div>
          <table><thead><tr><th>Track</th><th>Target</th><th>Range</th><th>Bearing</th><th>Time</th></tr></thead><tbody>${{rows}}</tbody></table>
        `;
      }}
      if (panel.plugin_id === "rpr") {{
        const fireRows = (panel.recent_weapon_fire || []).map((row) =>
          `<tr><td>${{row.interaction_class || ""}}</td><td>${{row.source || ""}}</td><td><code>${{JSON.stringify(row.parameters || {{}})}}</code></td></tr>`
        ).join("");
        const detRows = (panel.recent_detonations || []).map((row) =>
          `<tr><td>${{row.interaction_class || ""}}</td><td>${{row.source || ""}}</td><td><code>${{JSON.stringify(row.parameters || {{}})}}</code></td></tr>`
        ).join("");
        return `
          <div class="plugin-grid">
            <div class="plugin-card"><strong>Bridge Objects</strong><br>${{(panel.bridge_objects || []).length}}</div>
            <div class="plugin-card"><strong>WeaponFire</strong><br>${{panel.weapon_fire_count || 0}}</div>
            <div class="plugin-card"><strong>Detonations</strong><br>${{panel.detonation_count || 0}}</div>
          </div>
          <h3>Recent WeaponFire</h3>
          <table><thead><tr><th>Class</th><th>Source</th><th>Parameters</th></tr></thead><tbody>${{fireRows}}</tbody></table>
          <h3>Recent Detonations</h3>
          <table><thead><tr><th>Class</th><th>Source</th><th>Parameters</th></tr></thead><tbody>${{detRows}}</tbody></table>
        `;
      }}
      if (panel.plugin_id === "link16") {{
        const radioRows = (panel.radio_objects || []).map((row) =>
          `<tr><td>${{row.object_name || ""}}</td><td>${{row.attributes && JSON.stringify(row.attributes) || ""}}</td></tr>`
        ).join("");
        const jtidsRows = (panel.recent_jtids || []).map((row) =>
          `<tr><td>${{row.source || ""}}</td><td><code>${{JSON.stringify(row.parameters || {{}})}}</code></td></tr>`
        ).join("");
        const rttabRows = (panel.recent_rttab || []).map((row) =>
          `<tr><td>${{row.source || ""}}</td><td><code>${{JSON.stringify(row.parameters || {{}})}}</code></td></tr>`
        ).join("");
        return `
          <div class="plugin-grid">
            <div class="plugin-card"><strong>Radio Objects</strong><br>${{(panel.radio_objects || []).length}}</div>
            <div class="plugin-card"><strong>JTIDS Messages</strong><br>${{panel.jtids_count || 0}}</div>
            <div class="plugin-card"><strong>RTTAB Messages</strong><br>${{panel.rttab_count || 0}}</div>
          </div>
          <h3>Radio State</h3>
          <table><thead><tr><th>Object</th><th>Attributes</th></tr></thead><tbody>${{radioRows}}</tbody></table>
          <h3>Recent JTIDS</h3>
          <table><thead><tr><th>Source</th><th>Parameters</th></tr></thead><tbody>${{jtidsRows}}</tbody></table>
          <h3>Recent RTTAB</h3>
          <table><thead><tr><th>Source</th><th>Parameters</th></tr></thead><tbody>${{rttabRows}}</tbody></table>
        `;
      }}
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

    function appendEvent(event) {{
      if (lastPayload) {{
        const nextPayload = {{
          ...lastPayload,
          normalized_events: (lastPayload.normalized_events || []).concat([event]),
        }};
        renderState(nextPayload);
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
          backend: backendEl.value || null
          ,
          options: stepsEl.value ? {{ target_radar_steps: Number(stepsEl.value) }} : {{}}
        }})
      }});
      await refreshState();
    }};

    document.getElementById("stop-btn").onclick = async () => {{
      await fetch("/api/control/stop", {{ method: "POST" }});
      await refreshState();
    }};

    objectSelectEl.onchange = async () => {{
      const payload = lastPayload || await (await fetch("/api/state", {{ cache: "no-store" }})).json();
      const filters = activeFilters();
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
      const index = Number(objectSelectEl.value || "0");
      objectInspectorEl.textContent = objects[index] ? JSON.stringify(objects[index], null, 2) : "No object selected.";
    }};

    interactionSelectEl.onchange = async () => {{
      const payload = lastPayload || await (await fetch("/api/state", {{ cache: "no-store" }})).json();
      const filters = activeFilters();
      const interactions = ((payload.inspectors && payload.inspectors.interactions) || []).filter((row) => {{
        if (filters.family !== "all" && (row.family || "generic") !== filters.family) return false;
        if (filters.className !== "all" && (row.interaction_class || "") !== filters.className) return false;
        if (filters.eventType !== "all" && filters.eventType !== "interaction.received") return false;
        return true;
      }});
      const index = Number(interactionSelectEl.value || "0");
      interactionInspectorEl.textContent = interactions[index] ? JSON.stringify(interactions[index], null, 2) : "No interaction selected.";
    }};

    familyFilterEl.onchange = async () => refreshState();
    classFilterEl.onchange = async () => refreshState();
    eventTypeFilterEl.onchange = async () => refreshState();

    refreshState();
    const source = new EventSource("/events");
    source.onmessage = async (message) => {{
      appendEvent(JSON.parse(message.data));
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
    "RuntimeObserverControl",
    "RuntimeObserverSession",
    "build_runtime_observer_event_schema",
    "build_runtime_observer_catalog",
    "render_runtime_observer_html",
    "serve_runtime_observer",
]
