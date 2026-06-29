"""Reusable observer core for runtime showcase federation inspection."""
# pyright: reportReturnType=false, reportOptionalMemberAccess=false, reportCallIssue=false, reportArgumentType=false, reportAttributeAccessIssue=false
from __future__ import annotations

import importlib
import json
import multiprocessing
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from hla.verification.repo_internal.fom_tree_search import (
    build_fom_search_rows,
    build_fom_tree_nodes,
    describe_loaded_fom_modules,
)

from .runtime_event_stream import RuntimeEventStreamWriter
from .siso_runtime_showcase import build_siso_runtime_showcase_manifest, run_siso_runtime_showcase_scenario
from .target_radar_proof import write_target_radar_proof_artifacts
from .workspace_two_federate_suite import write_workspace_two_federate_suite_artifacts

RUNTIME_OBSERVER_EVENT_SCHEMA_VERSION = "runtime-observer-event-schema-v1"


def _append_ndjson(path: Path, row: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_jsonable(dict(row)), sort_keys=True) + "\n")


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
    if isinstance(value, (bytes, bytearray, memoryview)):
        text = _bytes_to_text_or_hex(bytes(value))
    else:
        text = str(value)
    text = text.rstrip("\x00").strip()
    return text or None


def _bytes_to_text_or_hex(value: bytes) -> str:
    try:
        decoded = value.decode("utf-8")
    except UnicodeDecodeError:
        return value.hex()
    normalized = decoded.rstrip("\x00")
    if normalized and all(character.isprintable() or character.isspace() for character in normalized):
        return normalized
    return value.hex()


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (bytes, bytearray, memoryview)):
        return _bytes_to_text_or_hex(bytes(value))
    return value


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


def _find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists() and (parent / "scripts" / "tools_federate_cli.py").exists():
            return parent
    raise RuntimeError("Could not locate repo root for runtime observer live-session bootstrap.")


def _bootstrap_repo_root() -> Path:
    repo_root = _find_repo_root()
    repo_text = str(repo_root)
    import sys

    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)
    return repo_root


def _load_federate_cli_module() -> Any:
    _bootstrap_repo_root()
    return importlib.import_module("scripts.tools_federate_cli")


def _call_surface(target: Any, *names: str, _args: tuple[Any, ...] = (), **kwargs: Any) -> Any:
    for name in names:
        method = getattr(target, name, None)
        if callable(method):
            return method(*_args, **kwargs)
    joined = " / ".join(name for name in names if name)
    raise AttributeError(f"{target!r} does not expose any of: {joined}")


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


def _build_class_tree_rows(specs: Mapping[str, Any], *, kind: str) -> list[dict[str, Any]]:
    return [
        {
            "full_name": row.full_name,
            "parent_name": row.parent_name,
            "depth": max(0, len(row.lineage) - 1),
            "kind": row.kind,
            "declared_members": list(row.declared_names),
            "all_members": list(row.total_names),
            "datatype_hints": list(row.datatype_hints),
            "lineage": list(row.lineage),
            "is_leaf": row.is_leaf,
        }
        for row in build_fom_tree_nodes(specs.values(), kind=kind)
    ]


def _build_fom_search_index(
    *,
    source_name: str,
    source_kind: str,
    object_specs: Mapping[str, Any] | None,
    interaction_specs: Mapping[str, Any] | None,
    datatype_names: Iterable[str],
    edition_classes: list[str],
    edition_scope: str,
    baseline_kinds: list[str],
    load_mode: str,
) -> list[dict[str, Any]]:
    object_nodes = build_fom_tree_nodes(() if object_specs is None else object_specs.values(), kind="object")
    interaction_nodes = build_fom_tree_nodes(() if interaction_specs is None else interaction_specs.values(), kind="interaction")
    return [
        {
            "source_name": row.source_name,
            "source_kind": row.source_kind,
            "kind": row.kind,
            "name": row.name,
            "parent_name": row.parent_name,
            "lineage": list(row.lineage),
            "is_leaf": row.is_leaf,
            "edition_classes": list(row.edition_classes),
            "edition_scope": row.edition_scope,
            "baseline_kinds": list(row.baseline_kinds),
            "load_mode": row.load_mode,
        }
        for row in build_fom_search_rows(
            source_name=source_name,
            source_kind=source_kind,
            object_nodes=object_nodes,
            interaction_nodes=interaction_nodes,
            datatype_names=datatype_names,
            edition_classes=edition_classes,
            edition_scope=edition_scope,
            baseline_kinds=baseline_kinds,
            load_mode=load_mode,
        )
    ]


def _build_loaded_fom_set(modules: Iterable[str], *, year: int | None) -> dict[str, Any] | None:
    descriptor = describe_loaded_fom_modules(modules, year=year)
    if descriptor is None:
        return None
    return dict(descriptor)


def _derive_federate_roster(inspectors: Mapping[str, Any], *, observer_name: str | None = None) -> list[dict[str, Any]]:
    roster: dict[str, dict[str, Any]] = {}
    if observer_name:
        roster[observer_name] = {
            "federate_name": observer_name,
            "role": "observer-self",
            "source": "session",
            "attributes": {},
        }
    for row in inspectors.get("objects", []):
        if not isinstance(row, Mapping):
            continue
        class_name = str(row.get("class_name", ""))
        if ".HLAmanager." not in class_name or not class_name.endswith("HLAfederate"):
            continue
        attributes = row.get("attributes") if isinstance(row.get("attributes"), Mapping) else {}
        federate_name = (
            _text_or_none(attributes.get("HLAfederateName"))
            or _text_or_none(row.get("object_name"))
            or _text_or_none(row.get("object_key"))
        )
        if federate_name is None:
            continue
        roster[federate_name] = {
            "federate_name": federate_name,
            "role": "mom-federate",
            "source": "mom",
            "attributes": dict(attributes),
        }
    return sorted(roster.values(), key=lambda row: row["federate_name"])


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
                        "fom_modules": row.get("fom_modules", []),
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
            {
                "provider": "live-federation",
                "label": "Live Federation Observer",
                "supports_live_callbacks": True,
                "scenarios": [
                    {
                        "id": "live-federation",
                        "label": "Live Federation Observer",
                        "story": "Join an existing federation execution late, subscribe broadly from the supplied FOM set, and retain local observer history and snapshots.",
                        "default_options": {
                            "edition": "2010",
                            "federate_name": "FederationObserver",
                            "federate_type": "observer",
                            "poll_seconds": 0.25,
                        },
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

    def events(self, *, after_sequence: int = 0) -> list[dict[str, Any]]:
        self._refresh_status()
        return _events_after(_load_ndjson(self.paths.trace_ndjson), after_sequence)

    def live_state(self) -> dict[str, Any]:
        self._refresh_status()
        with self._lock:
            status = self._status
            error = self._error
        summary = _load_json(self.paths.summary_json)
        events = _load_ndjson(self.paths.trace_ndjson)
        metrics = _derive_live_metrics(events)
        normalized_events = [_normalize_event(event) for event in events]
        runtime_edition = self.spec.metadata.get("runtime_edition")
        loaded_fom_set = _build_loaded_fom_set(
            tuple(str(item) for item in self.spec.metadata.get("fom_modules", []) or ()),
            year=int(runtime_edition) if isinstance(runtime_edition, str) and runtime_edition.isdigit() else None,
        )
        inspectors = _derive_generic_inspectors(
            {
                "provider": self.spec.provider,
                "scenario": self.spec.scenario,
                "final_summary": summary,
            },
            normalized_events,
        )
        plugin_panels = []
        for plugin in (
            _derive_target_radar_plugin(
                {
                    "provider": self.spec.provider,
                    "scenario": self.spec.scenario,
                    "final_summary": summary,
                },
                normalized_events,
            ),
            _derive_rpr_plugin(
                {
                    "provider": self.spec.provider,
                    "scenario": self.spec.scenario,
                    "family": self.spec.metadata.get("family"),
                },
                inspectors,
            ),
            _derive_link16_plugin(
                {
                    "provider": self.spec.provider,
                    "scenario": self.spec.scenario,
                    "family": self.spec.metadata.get("family"),
                },
                inspectors,
            ),
        ):
            if plugin is not None:
                plugin_panels.append(plugin)
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
            "loaded_fom_set": loaded_fom_set,
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


class LiveRuntimeObserverSession:
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
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.backend = backend
        self.options = dict(options or {})
        self.trace_ndjson = self.output_dir / "runtime_observer_trace.ndjson"
        self.summary_json = self.output_dir / "live_observer_summary.json"
        self.snapshot_json = self.output_dir / "live_observer_snapshot.json"
        self.history_ndjson = self.output_dir / "observer_history.ndjson"
        self.federate_cli = _load_federate_cli_module()
        edition = str(self.options.get("edition", "2010"))
        backend_name = str(self.options.get("backend") or backend or ("python1516_2025" if edition == "2025" else "python1516e"))
        federation_name = str(self.options.get("federation_name") or f"live-observer-{edition}")
        federate_name = str(self.options.get("federate_name") or "FederationObserver")
        federate_type = str(self.options.get("federate_type") or "observer")
        fom_modules = tuple(str(item) for item in self.options.get("fom_modules", []) or ())
        logical_time_implementation = str(self.options.get("logical_time_implementation") or "HLAinteger64Time")
        transport_kind = self.options.get("transport_kind")
        transport_target = self.options.get("transport_target")
        self.config = self.federate_cli.SessionConfig(
            edition=edition,
            backend=backend_name,
            federation_name=federation_name,
            federate_name=federate_name,
            federate_type=federate_type,
            fom_modules=fom_modules,
            logical_time_implementation=logical_time_implementation,
            transport_kind=None if transport_kind is None else str(transport_kind),
            transport_target=None if transport_target is None else str(transport_target),
            json_output=False,
        )
        self.session = self.federate_cli.InteractiveFederateSession(config=self.config)
        self.writer = RuntimeEventStreamWriter(self.trace_ndjson)
        self._lock = threading.Lock()
        self._status = "created"
        self._error: str | None = None
        self._stop_event = threading.Event()
        self._worker: threading.Thread | None = None
        self._seen_callbacks = 0
        self._object_handle_classes: dict[str, str] = {}
        self._object_name_classes: dict[str, str] = {}

    def start(self) -> None:
        with self._lock:
            self._status = "running"
        self._worker = threading.Thread(target=self._run, name="runtime-observer-live", daemon=True)
        self._worker.start()

    def stop(self) -> None:
        self._stop_event.set()
        worker = self._worker
        if worker is not None:
            worker.join(timeout=2.0)
        try:
            self.session.close()
        except Exception:
            pass
        with self._lock:
            if self._status == "running":
                self._status = "stopped"

    def _emit(self, event: Mapping[str, Any]) -> None:
        self.writer.emit(event)
        payload = {"recorded_at": time.time(), **dict(event)}
        _append_ndjson(self.history_ndjson, payload)

    def _snapshot(self) -> dict[str, Any]:
        raw_events = _load_ndjson(self.trace_ndjson)
        history_events = _load_ndjson(self.history_ndjson)
        combined_events = history_events if history_events else raw_events
        normalized_events = [_normalize_event(event) for event in combined_events]
        inspectors = _derive_generic_inspectors(
            {
                "provider": self.spec.provider,
                "scenario": self.spec.scenario,
                "final_summary": _load_json(self.summary_json),
            },
            normalized_events,
        )
        fom_catalog = getattr(self.session, "fom_catalog", None)
        loaded_fom_set = _build_loaded_fom_set(self.config.fom_modules, year=int(self.config.edition) if str(self.config.edition).isdigit() else None)
        object_specs = None if fom_catalog is None else fom_catalog.object_classes
        interaction_specs = None if fom_catalog is None else fom_catalog.interaction_classes
        datatype_names = [] if fom_catalog is None else sorted(fom_catalog.datatype_names)
        fom_tree = {
            "object_classes": [] if object_specs is None else _build_class_tree_rows(object_specs, kind="object"),
            "interaction_classes": [] if interaction_specs is None else _build_class_tree_rows(interaction_specs, kind="interaction"),
            "datatypes": datatype_names,
            "search_index": _build_fom_search_index(
                source_name=self.spec.scenario,
                source_kind="live-federation",
                object_specs=object_specs,
                interaction_specs=interaction_specs,
                datatype_names=datatype_names,
                edition_classes=[] if loaded_fom_set is None else list(loaded_fom_set.get("edition_classes", [])),
                edition_scope="schema-only / support-only" if loaded_fom_set is None else str(loaded_fom_set.get("edition_scope", "schema-only / support-only")),
                baseline_kinds=[] if loaded_fom_set is None else list(loaded_fom_set.get("baseline_kinds", [])),
                load_mode="custom-live",
            ),
        }
        live_metrics = _derive_live_metrics(raw_events)
        state = {
            "provider": self.spec.provider,
            "scenario": self.spec.scenario,
            "label": self.spec.label,
            "story": self.spec.story,
            "supports_live_callbacks": True,
            "participant_profiles": self.spec.participant_profiles,
            "backend": self.config.backend,
            "options": dict(self.options),
            "status": self._status,
            "error": self._error,
            "summary_ready": self.summary_json.exists(),
            "listener_report_ready": False,
            "artifacts": {
                "trace_ndjson": str(self.trace_ndjson),
                "summary_json": str(self.summary_json),
                "snapshot_json": str(self.snapshot_json),
                "history_ndjson": str(self.history_ndjson),
            },
            "live_metrics": live_metrics,
            "final_summary": _load_json(self.summary_json),
            "catalog_metadata": self.spec.metadata,
            "inspectors": inspectors,
            "plugin_panels": [],
            "normalized_events": normalized_events,
            "schema_version": RUNTIME_OBSERVER_EVENT_SCHEMA_VERSION,
            "federate_roster": _derive_federate_roster(inspectors, observer_name=self.config.federate_name),
            "fom_tree": fom_tree,
            "loaded_fom_set": loaded_fom_set,
            "history_event_count": len(history_events),
        }
        for plugin in (
            _derive_target_radar_plugin(state, normalized_events),
            _derive_rpr_plugin({"family": _text_or_none(self.options.get("family")) or "generic", "scenario": self.spec.scenario}, inspectors),
            _derive_link16_plugin({"family": _text_or_none(self.options.get("family")) or "generic"}, inspectors),
        ):
            if plugin is not None:
                state["plugin_panels"].append(plugin)
        self.snapshot_json.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.summary_json.write_text(
            json.dumps(
                {
                    "observer_name": self.config.federate_name,
                    "federation_name": self.config.federation_name,
                    "edition": self.config.edition,
                    "backend": self.config.backend,
                    "fom_module_count": len(self.config.fom_modules),
                    "live_metrics": live_metrics,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return state

    def _subscribe_all_from_catalog(self) -> None:
        catalog = self.session._ensure_fom_catalog()
        if catalog is None:
            return
        for full_name, spec in sorted(catalog.object_classes.items()):
            try:
                self.session.subscribe_object(full_name, tuple(spec.attributes))
            except Exception:
                continue
        for full_name in sorted(catalog.interaction_classes):
            try:
                self.session.subscribe_interaction(full_name)
            except Exception:
                continue

    def _decode_callback_record(self, record: Any) -> dict[str, Any]:
        method_name = str(record.method_name)
        args = tuple(record.args)
        event: dict[str, Any] = {
            "kind": "callback",
            "provider": self.spec.provider,
            "scenario": self.spec.scenario,
            "callback": method_name,
            "listener_name": self.config.federate_name,
            "listener_role": self.config.federate_type,
        }
        try:
            if method_name == "discoverObjectInstance" and len(args) >= 3:
                event["entity_handle_text"] = str(args[0])
                event["class_handle_text"] = str(args[1])
                event["entity_name"] = str(args[2])
                class_name = _call_surface(self.session.rti, "getObjectClassName", "get_object_class_name", _args=(args[1],))
                event["class_name"] = class_name
                self._object_handle_classes[str(args[0])] = str(class_name)
                self._object_name_classes[str(args[2])] = str(class_name)
            elif method_name == "reflectAttributeValues" and len(args) >= 2:
                object_handle = args[0]
                attribute_values = args[1] if isinstance(args[1], Mapping) else {}
                class_name = None
                try:
                    object_name = _call_surface(self.session.rti, "getObjectInstanceName", "get_object_instance_name", _args=(object_handle,))
                except Exception:
                    object_name = None
                event["entity_handle_text"] = str(object_handle)
                if object_name is not None:
                    event["entity_name"] = str(object_name)
                class_name = self._object_handle_classes.get(str(object_handle))
                if class_name is None and object_name is not None:
                    class_name = self._object_name_classes.get(str(object_name))
                decoded_values: dict[str, Any] = {}
                for handle, value in attribute_values.items():
                    try:
                        if class_name is None and object_name is not None and getattr(self.session, "state", None) is not None:
                            class_name = self.session.state.object_instance_classes.get(object_name)
                        class_handle = None if class_name is None else _call_surface(self.session.rti, "getObjectClassHandle", "get_object_class_handle", _args=(class_name,))
                        attribute_name = (
                            str(handle)
                            if class_handle is None
                            else _call_surface(self.session.rti, "getAttributeName", "get_attribute_name", _args=(class_handle, handle))
                        )
                    except Exception:
                        attribute_name = str(handle)
                    decoded_values[attribute_name] = value
                if class_name is not None:
                    event["class_name"] = str(class_name)
                event["values"] = decoded_values
                if len(args) >= 3:
                    event["tag"] = args[2]
            elif method_name == "receiveInteraction" and len(args) >= 2:
                interaction_handle = args[0]
                parameter_values = args[1] if isinstance(args[1], Mapping) else {}
                interaction_class_name = _call_surface(
                    self.session.rti,
                    "getInteractionClassName",
                    "get_interaction_class_name",
                    _args=(interaction_handle,),
                )
                event["class_handle_text"] = str(interaction_handle)
                event["class_name"] = interaction_class_name
                decoded_values: dict[str, Any] = {}
                for handle, value in parameter_values.items():
                    try:
                        parameter_name = _call_surface(
                            self.session.rti,
                            "getParameterName",
                            "get_parameter_name",
                            _args=(interaction_handle, handle),
                        )
                    except Exception:
                        parameter_name = str(handle)
                    decoded_values[parameter_name] = value
                event["values"] = decoded_values
                if len(args) >= 3:
                    event["tag"] = args[2]
            else:
                event["payload"] = {"args": [repr(item) for item in args], "kwargs": dict(record.kwargs)}
        except Exception as exc:
            event["payload"] = {"decode_error": repr(exc), "args": [repr(item) for item in args], "kwargs": dict(record.kwargs)}
        return event

    def _run(self) -> None:
        try:
            self.session.connect()
            self._emit({"kind": "operation", "provider": self.spec.provider, "scenario": self.spec.scenario, "operation": "connect", "actor": self.config.federate_name})
            self.session.join(
                federate_name=self.config.federate_name,
                federate_type=self.config.federate_type,
                federation_name=self.config.federation_name,
                create_if_missing=False,
            )
            self._emit(
                {
                    "kind": "operation",
                    "provider": self.spec.provider,
                    "scenario": self.spec.scenario,
                    "operation": "join-federation",
                    "actor": self.config.federate_name,
                    "target": self.config.federation_name,
                    "details": {"edition": self.config.edition, "backend": self.config.backend},
                }
            )
            if self.config.fom_modules:
                try:
                    self.session._load_fom_catalog(self.config.fom_modules)
                except Exception:
                    pass
            self._subscribe_all_from_catalog()
            self._emit({"kind": "phase", "provider": self.spec.provider, "scenario": self.spec.scenario, "phase": "observer-subscribed"})
            while not self._stop_event.is_set():
                self.session.evoke(0.0, 0.0)
                records = [] if self.session.callbacks is None else self.session.callbacks.records[self._seen_callbacks :]
                for record in records:
                    self._emit(self._decode_callback_record(record))
                self._seen_callbacks += len(records)
                self._snapshot()
                time.sleep(float(self.options.get("poll_seconds", 0.25)))
            with self._lock:
                self._status = "stopped"
        except Exception as exc:
            with self._lock:
                self._status = "failed"
                self._error = repr(exc)
            self._snapshot()

    def events(self, *, after_sequence: int = 0) -> list[dict[str, Any]]:
        return _events_after(_load_ndjson(self.trace_ndjson), after_sequence)

    def live_state(self) -> dict[str, Any]:
        return self._snapshot()


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
            return self._session

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
            spec = _resolve_spec(provider, scenario)
            merged_options = {**dict(spec.metadata.get("default_options", {})), **dict(options or {})}
            session_cls: type[RuntimeObserverSession | LiveRuntimeObserverSession]
            session_cls = LiveRuntimeObserverSession if provider == "live-federation" else RuntimeObserverSession
            session = session_cls(
                provider=provider,
                scenario=scenario,
                output_dir=self.output_dir / provider / scenario,
                backend=backend or self.default_backend,
                options=merged_options,
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


__all__ = [
    "LiveRuntimeObserverSession",
    "RUNTIME_OBSERVER_EVENT_SCHEMA_VERSION",
    "RuntimeObserverControl",
    "RuntimeObserverSession",
    "build_runtime_observer_catalog",
    "build_runtime_observer_event_schema",
    "_derive_generic_inspectors",
    "_derive_link16_plugin",
    "_derive_live_metrics",
    "_derive_rpr_plugin",
    "_derive_target_radar_plugin",
    "_normalize_event",
    "_resolve_spec",
    "_text_or_none",
]
