"""Runtime listener helpers for small executable HLA showcase scenarios."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from hla.backends.common import RecordingFederateAmbassador


def _jsonable(value: Any) -> Any:
    if isinstance(value, bytes):
        decoded = value.decode("utf-8", errors="replace").rstrip("\x00")
        if decoded and all(character.isprintable() for character in decoded):
            return decoded
        return value.hex()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _html_escape(value: Any) -> str:
    text = str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


@dataclass(frozen=True)
class RuntimeListenerPaths:
    scenario_dir: Path
    trace_ndjson: Path
    summary_json: Path
    report_html: Path


class RuntimeListenerSession:
    """Incremental listener event recorder with operator-facing artifacts."""

    def __init__(
        self,
        *,
        scenario: str,
        family: str,
        runtime_edition: str,
        topology: str,
        federation_name: str,
        backend: str,
        fom_modules: list[str],
        participants: list[dict[str, Any]],
        story: str,
        output_root: str | Path | None = None,
    ) -> None:
        self.metadata = {
            "scenario": scenario,
            "family": family,
            "runtime_edition": runtime_edition,
            "topology": topology,
            "federation_name": federation_name,
            "backend": backend,
            "fom_modules": list(fom_modules),
            "participants": list(participants),
            "story": story,
        }
        self.events: list[dict[str, Any]] = []
        self.discovered_objects: list[dict[str, Any]] = []
        self.reflections: list[dict[str, Any]] = []
        self.interactions: list[dict[str, Any]] = []
        self.statistics = {
            "phases": 0,
            "operations": 0,
            "callbacks": {
                "discoverObjectInstance": 0,
                "reflectAttributeValues": 0,
                "receiveInteraction": 0,
            },
        }
        self.paths: RuntimeListenerPaths | None = None
        if output_root is not None:
            scenario_dir = Path(output_root) / scenario
            scenario_dir.mkdir(parents=True, exist_ok=True)
            self.paths = RuntimeListenerPaths(
                scenario_dir=scenario_dir,
                trace_ndjson=scenario_dir / "listener_trace.ndjson",
                summary_json=scenario_dir / "listener_summary.json",
                report_html=scenario_dir / "listener_report.html",
            )
            self.paths.trace_ndjson.write_text("", encoding="utf-8")

    def _append_event(self, event: dict[str, Any]) -> None:
        payload = {"sequence": len(self.events) + 1, **event}
        self.events.append(payload)
        if self.paths is not None:
            with self.paths.trace_ndjson.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(_jsonable(payload), sort_keys=True) + "\n")

    def mark_phase(self, phase: str, *, metrics: Mapping[str, Any] | None = None) -> None:
        self.statistics["phases"] += 1
        self._append_event({"kind": "phase", "phase": phase, "metrics": _jsonable(metrics or {})})

    def record_operation(
        self,
        operation: str,
        *,
        actor: str,
        target: str,
        tag: bytes | str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        self.statistics["operations"] += 1
        self._append_event(
            {
                "kind": "operation",
                "operation": operation,
                "actor": actor,
                "target": target,
                "tag": _jsonable(tag),
                "details": _jsonable(details or {}),
            }
        )

    def record_callback(
        self,
        callback_name: str,
        *,
        listener_name: str,
        listener_role: str,
        entity_name: str | None = None,
        entity_handle_text: str | None = None,
        class_name: str | None = None,
        class_handle_text: str | None = None,
        tag: bytes | str | None = None,
        values: Mapping[str, Any] | None = None,
        producing_federate: Any | None = None,
    ) -> None:
        if callback_name in self.statistics["callbacks"]:
            self.statistics["callbacks"][callback_name] += 1
        event = {
            "kind": "callback",
            "callback": callback_name,
            "listener_name": listener_name,
            "listener_role": listener_role,
            "entity_name": entity_name,
            "entity_handle_text": entity_handle_text,
            "class_name": class_name,
            "class_handle_text": class_handle_text,
            "tag": _jsonable(tag),
            "values": _jsonable(values or {}),
            "producing_federate": _jsonable(producing_federate),
        }
        self._append_event(event)
        if callback_name == "discoverObjectInstance":
            self.discovered_objects.append(event)
        elif callback_name == "reflectAttributeValues":
            self.reflections.append(event)
        elif callback_name == "receiveInteraction":
            self.interactions.append(event)

    def finalize(
        self,
        *,
        lifecycle: list[str],
        operation_attempts: Mapping[str, Any],
        execution_complete: bool,
        status: str,
    ) -> dict[str, Any]:
        summary = {
            **self.metadata,
            "lifecycle": list(lifecycle),
            "operation_attempts": _jsonable(operation_attempts),
            "execution_complete": execution_complete,
            "status": status,
            "statistics": _jsonable(self.statistics),
            "discovered_objects": _jsonable(self.discovered_objects),
            "reflections": _jsonable(self.reflections),
            "interactions": _jsonable(self.interactions),
            "event_count": len(self.events),
            "events": _jsonable(self.events),
            "artifacts": (
                {
                    "trace_ndjson": str(self.paths.trace_ndjson),
                    "summary_json": str(self.paths.summary_json),
                    "report_html": str(self.paths.report_html),
                }
                if self.paths is not None
                else {}
            ),
        }
        if self.paths is not None:
            self.paths.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            self.paths.report_html.write_text(self._render_html(summary), encoding="utf-8")
        return summary

    def _render_html(self, summary: Mapping[str, Any]) -> str:
        participant_rows = "\n".join(
            "<tr>"
            f"<td>{_html_escape(row['federate'])}</td>"
            f"<td>{_html_escape(row['role'])}</td>"
            f"<td>{_html_escape(row.get('posture', ''))}</td>"
            f"<td>{_html_escape(', '.join(row.get('publishes', [])))}</td>"
            f"<td>{_html_escape(', '.join(row.get('subscribes', [])))}</td>"
            "</tr>"
            for row in summary["participants"]
        )
        event_rows = "\n".join(
            "<tr>"
            f"<td>{_html_escape(row['sequence'])}</td>"
            f"<td>{_html_escape(row['kind'])}</td>"
            f"<td>{_html_escape(row.get('phase') or row.get('operation') or row.get('callback') or '')}</td>"
            f"<td>{_html_escape(row.get('actor') or row.get('listener_name') or '')}</td>"
            f"<td><code>{_html_escape(json.dumps(_jsonable(row), sort_keys=True))}</code></td>"
            "</tr>"
            for row in summary["events"]
        )
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{_html_escape(summary['scenario'])} listener report</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f1e8;
      --panel: #fffdfa;
      --ink: #1f2933;
      --accent: #9f3a16;
      --grid: #d7cbb8;
    }}
    body {{ margin: 0; font: 15px/1.5 Menlo, Consolas, monospace; background: linear-gradient(160deg, #efe7d2, var(--bg)); color: var(--ink); }}
    main {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
    section {{ background: var(--panel); border: 1px solid var(--grid); border-radius: 16px; padding: 16px 18px; margin-bottom: 18px; box-shadow: 0 10px 30px rgba(31,41,51,0.08); }}
    h1, h2 {{ margin: 0 0 12px; }}
    h1 {{ color: var(--accent); }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid var(--grid); padding: 8px 10px; text-align: left; vertical-align: top; }}
    code {{ white-space: pre-wrap; word-break: break-word; }}
    .stats {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }}
    .stat {{ border: 1px solid var(--grid); border-radius: 12px; padding: 12px; background: #fff8ef; }}
    ul {{ margin: 0; padding-left: 18px; }}
  </style>
</head>
<body>
  <main>
    <section>
      <h1>{_html_escape(summary['scenario'])}</h1>
      <p>{_html_escape(summary['story'])}</p>
      <p>Edition: <strong>{_html_escape(summary['runtime_edition'])}</strong> |
         Family: <strong>{_html_escape(summary['family'])}</strong> |
         Topology: <strong>{_html_escape(summary['topology'])}</strong> |
         Backend: <strong>{_html_escape(summary['backend'])}</strong></p>
      <p>Federation: <code>{_html_escape(summary['federation_name'])}</code></p>
      <p>FOM modules: <code>{_html_escape(', '.join(summary['fom_modules']))}</code></p>
    </section>
    <section>
      <h2>Runtime Stats</h2>
      <div class="stats">
        <div class="stat"><strong>Phases</strong><br>{_html_escape(summary['statistics']['phases'])}</div>
        <div class="stat"><strong>Operations</strong><br>{_html_escape(summary['statistics']['operations'])}</div>
        <div class="stat"><strong>Discoveries</strong><br>{_html_escape(summary['statistics']['callbacks']['discoverObjectInstance'])}</div>
        <div class="stat"><strong>Reflections / Interactions</strong><br>{_html_escape(summary['statistics']['callbacks']['reflectAttributeValues'])} / {_html_escape(summary['statistics']['callbacks']['receiveInteraction'])}</div>
      </div>
    </section>
    <section>
      <h2>Participants</h2>
      <table>
        <thead><tr><th>Federate</th><th>Role</th><th>Posture</th><th>Publishes</th><th>Subscribes</th></tr></thead>
        <tbody>{participant_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Lifecycle</h2>
      <ul>{"".join(f"<li>{_html_escape(item)}</li>" for item in summary['lifecycle'])}</ul>
    </section>
    <section>
      <h2>Event Timeline</h2>
      <table>
        <thead><tr><th>#</th><th>Kind</th><th>Label</th><th>Actor / Listener</th><th>Details</th></tr></thead>
        <tbody>{event_rows}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


class RuntimeListenerFederate(RecordingFederateAmbassador):
    """Recording federate ambassador that projects callback traffic into a listener session."""

    def __init__(self, session: RuntimeListenerSession, *, federate_name: str, role: str) -> None:
        super().__init__()
        self._session = session
        self._federate_name = federate_name
        self._role = role

    def on_discover_object_instance(self, *args: Any, **kwargs: Any) -> None:
        producing_federate = args[3] if len(args) > 3 else kwargs.get("producingFederate")
        self._session.record_callback(
            "discoverObjectInstance",
            listener_name=self._federate_name,
            listener_role=self._role,
            entity_name=str(args[2]) if len(args) > 2 else None,
            entity_handle_text=repr(args[0]) if args else None,
            class_name=repr(args[1]) if len(args) > 1 else None,
            class_handle_text=repr(args[1]) if len(args) > 1 else None,
            producing_federate=producing_federate,
        )

    def on_reflect_attribute_values(self, *args: Any, **kwargs: Any) -> None:
        attributes = args[1] if len(args) > 1 else {}
        tag = args[2] if len(args) > 2 else kwargs.get("userSuppliedTag")
        self._session.record_callback(
            "reflectAttributeValues",
            listener_name=self._federate_name,
            listener_role=self._role,
            entity_name=None,
            entity_handle_text=repr(args[0]) if args else None,
            tag=tag,
            values={str(key): _jsonable(value) for key, value in dict(attributes).items()},
        )

    def on_receive_interaction(self, *args: Any, **kwargs: Any) -> None:
        parameters = args[1] if len(args) > 1 else {}
        tag = args[2] if len(args) > 2 else kwargs.get("userSuppliedTag")
        producing_federate = None
        if len(args) > 4:
            producing_federate = args[4]
        self._session.record_callback(
            "receiveInteraction",
            listener_name=self._federate_name,
            listener_role=self._role,
            class_name=repr(args[0]) if args else None,
            class_handle_text=repr(args[0]) if args else None,
            tag=tag,
            values={str(key): _jsonable(value) for key, value in dict(parameters).items()},
            producing_federate=producing_federate,
        )


__all__ = [
    "RuntimeListenerFederate",
    "RuntimeListenerPaths",
    "RuntimeListenerSession",
]
