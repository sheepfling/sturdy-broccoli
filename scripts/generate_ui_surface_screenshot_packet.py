from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path
from typing import Any

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla.verification.repo_internal.fom_workbench import write_fom_workbench_html
from hla.verification.repo_internal.verification.federate_service_fastapi import create_federate_service_fastapi_app
from hla.verification.repo_internal.verification.runtime_observer_core import build_runtime_observer_catalog
from hla.verification.repo_internal.verification.runtime_observer_fastapi import create_runtime_observer_fastapi_app
from hla.verification.repo_internal.verification.ui_surface_capture import (
    capture_live_federate_service,
    capture_live_visualizer,
    launch_browser,
    run_local_app,
    write_gallery_index,
    write_gallery_manifest,
)


class _StaticObserverControl:
    def __init__(self, state: dict[str, Any]) -> None:
        self._state = state
        self._catalog = build_runtime_observer_catalog()
        self._events = [
            {
                "sequence": 1,
                "kind": "callback",
                "provider": state.get("provider"),
                "scenario": state.get("scenario"),
                "callback": "discoverObjectInstance",
                "entity_name": "Track-001",
                "entity_handle_text": "ObjectInstanceHandle(101)",
                "class_name": "HLAobjectRoot.BaseEntity.PhysicalEntity.Platform.Aircraft",
                "class_handle_text": "ObjectClassHandle(11)",
                "listener_name": "Observer1",
                "listener_role": "observer",
            }
        ]

    def current_session(self) -> object:
        return object()

    def state(self) -> dict[str, Any]:
        return dict(self._state)

    def catalog(self) -> dict[str, Any]:
        return self._catalog

    def events(self, *, after_sequence: int = 0) -> list[dict[str, Any]]:
        return [row for row in self._events if int(row.get("sequence", 0)) > after_sequence]

    def start(
        self,
        *,
        provider: str,
        scenario: str,
        backend: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> "_StaticObserverControl":
        return self

    def stop(self) -> dict[str, Any]:
        return {"status": "stopped"}


def _demo_runtime_observer_state() -> dict[str, Any]:
    return {
        "provider": "live-federation",
        "scenario": "live-federation",
        "label": "Hydrated Federation Visualizer Fixture",
        "story": "Seeded observer state for deterministic UI screenshot regeneration.",
        "supports_live_callbacks": True,
        "participant_profiles": [
            {
                "federate": "Shooter1",
                "role": "entity-publisher",
                "publishes": ["Aircraft", "WeaponFire"],
                "subscribes": ["TrackReport"],
            },
            {
                "federate": "Observer1",
                "role": "observer",
                "publishes": [],
                "subscribes": ["Aircraft", "TrackReport", "WeaponFire"],
            },
        ],
        "backend": "python1516e",
        "options": {
            "edition": "2010",
            "federation_name": "demo-fed",
            "federate_name": "Observer1",
            "fom_modules": ["DemoFOMmodule.xml"],
        },
        "status": "running",
        "error": None,
        "summary_ready": True,
        "listener_report_ready": False,
        "artifacts": {
            "trace_ndjson": "artifacts/federation_visualizer/runtime_observer_trace.ndjson",
            "summary_json": "artifacts/federation_visualizer/live_observer_summary.json",
            "snapshot_json": "artifacts/federation_visualizer/live_observer_snapshot.json",
            "history_ndjson": "artifacts/federation_visualizer/observer_history.ndjson",
        },
        "live_metrics": {
            "event_count": 8,
            "phases": ["observer-subscribed", "steady-state"],
            "last_phase": "steady-state",
            "operations": 2,
            "callbacks": {
                "discoverObjectInstance": 2,
                "reflectAttributeValues": 2,
                "receiveInteraction": 2,
            },
        },
        "final_summary": {
            "observer_name": "Observer1",
            "federation_name": "demo-fed",
            "edition": "2010",
            "backend": "python1516e",
        },
        "catalog_metadata": {"id": "live-federation"},
        "inspectors": {
            "objects": [
                {
                    "object_key": "ObjectInstanceHandle(101)",
                    "object_id": "ObjectInstanceHandle(101)",
                    "object_name": "Track-001",
                    "object_handle_text": "ObjectInstanceHandle(101)",
                    "class_name": "HLAobjectRoot.BaseEntity.PhysicalEntity.Platform.Aircraft",
                    "class_handle_text": "ObjectClassHandle(11)",
                    "family": "rpr",
                    "attributes": {"Callsign": "EAGLE11", "Altitude": "12000"},
                    "update_count": 3,
                    "discovery_count": 1,
                    "last_tag": "RPR",
                    "sources": ["Observer1"],
                    "aliases": ["Track-001"],
                },
                {
                    "object_key": "ObjectInstanceHandle(102)",
                    "object_id": "ObjectInstanceHandle(102)",
                    "object_name": "ObserverMomObject",
                    "object_handle_text": "ObjectInstanceHandle(102)",
                    "class_name": "HLAobjectRoot.HLAmanager.HLAfederation.HLAfederate",
                    "class_handle_text": "ObjectClassHandle(99)",
                    "family": "generic",
                    "attributes": {"HLAfederateName": "Shooter1"},
                    "update_count": 1,
                    "discovery_count": 1,
                    "last_tag": "MOM",
                    "sources": ["Observer1"],
                    "aliases": ["Shooter1"],
                },
            ],
            "interactions": [
                {
                    "interaction_key": "WeaponFire::1",
                    "interaction_class": "WeaponFire",
                    "class_handle_text": "InteractionClassHandle(7)",
                    "family": "rpr",
                    "source": "Shooter1",
                    "observer_role": "observer",
                    "tag": "WF",
                    "parameters": {"TargetObjectIdentifier": "Track-001"},
                },
                {
                    "interaction_key": "TrackReport::2",
                    "interaction_class": "TrackReport",
                    "class_handle_text": "InteractionClassHandle(8)",
                    "family": "target-radar",
                    "source": "Observer1",
                    "observer_role": "observer",
                    "tag": "TRK",
                    "parameters": {"track_id": "Track-001", "quality": "firm"},
                },
            ],
        },
        "plugin_panels": [
            {
                "plugin_id": "rpr",
                "title": "RPR Engagement Panel",
                "bridge_objects": [{"name": "Bridge-Alpha"}],
                "weapon_fire_count": 1,
                "detonation_count": 0,
            }
        ],
        "normalized_events": [
            {
                "sequence": 1,
                "event_type": "object.discovered",
                "provider": "live-federation",
                "scenario": "live-federation",
                "family": "rpr",
                "object_key": "ObjectInstanceHandle(101)",
                "object_name": "Track-001",
                "object_handle_text": "ObjectInstanceHandle(101)",
                "class_name": "HLAobjectRoot.BaseEntity.PhysicalEntity.Platform.Aircraft",
            },
            {
                "sequence": 2,
                "event_type": "object.updated",
                "provider": "live-federation",
                "scenario": "live-federation",
                "family": "rpr",
                "object_key": "ObjectInstanceHandle(101)",
                "class_name": "HLAobjectRoot.BaseEntity.PhysicalEntity.Platform.Aircraft",
                "attributes": {"Callsign": "EAGLE11"},
            },
            {
                "sequence": 3,
                "event_type": "interaction.received",
                "provider": "live-federation",
                "scenario": "live-federation",
                "family": "rpr",
                "interaction_key": "WeaponFire::1",
                "interaction_class": "WeaponFire",
                "parameters": {"TargetObjectIdentifier": "Track-001"},
            },
        ],
        "schema_version": "runtime-observer-event-schema-v1",
        "federate_roster": [
            {"federate_name": "Observer1", "role": "observer-self", "source": "session", "attributes": {}},
            {"federate_name": "Shooter1", "role": "mom-federate", "source": "mom", "attributes": {"HLAfederateName": "Shooter1"}},
        ],
        "fom_tree": {
            "object_classes": [
                {
                    "full_name": "HLAobjectRoot.BaseEntity",
                    "parent_name": "HLAobjectRoot",
                    "depth": 1,
                    "kind": "object",
                    "declared_members": ["EntityIdentifier"],
                    "all_members": ["EntityIdentifier"],
                    "datatype_hints": ["EntityIdentifierStruct"],
                    "lineage": ["HLAobjectRoot.BaseEntity"],
                    "is_leaf": False,
                },
                {
                    "full_name": "HLAobjectRoot.BaseEntity.PhysicalEntity.Platform.Aircraft",
                    "parent_name": "HLAobjectRoot.BaseEntity",
                    "depth": 4,
                    "kind": "object",
                    "declared_members": ["Callsign", "Altitude"],
                    "all_members": ["EntityIdentifier", "Callsign", "Altitude"],
                    "datatype_hints": ["HLAunicodeString", "AltitudeStruct"],
                    "lineage": [
                        "HLAobjectRoot.BaseEntity",
                        "HLAobjectRoot.BaseEntity.PhysicalEntity.Platform.Aircraft",
                    ],
                    "is_leaf": True,
                },
                {
                    "full_name": "HLAobjectRoot.HLAmanager.HLAfederation.HLAfederate",
                    "parent_name": "HLAobjectRoot.HLAmanager.HLAfederation",
                    "depth": 3,
                    "kind": "object",
                    "declared_members": ["HLAfederateName"],
                    "all_members": ["HLAfederateName"],
                    "datatype_hints": ["HLAunicodeString"],
                    "lineage": ["HLAobjectRoot.HLAmanager.HLAfederation.HLAfederate"],
                    "is_leaf": True,
                },
            ],
            "interaction_classes": [
                {
                    "full_name": "WeaponFire",
                    "parent_name": "HLAinteractionRoot",
                    "depth": 0,
                    "kind": "interaction",
                    "declared_members": ["TargetObjectIdentifier"],
                    "all_members": ["TargetObjectIdentifier"],
                    "datatype_hints": ["RTIobjectIdStruct"],
                    "lineage": ["WeaponFire"],
                    "is_leaf": True,
                },
                {
                    "full_name": "TrackReport",
                    "parent_name": "HLAinteractionRoot",
                    "depth": 0,
                    "kind": "interaction",
                    "declared_members": ["track_id", "quality"],
                    "all_members": ["track_id", "quality"],
                    "datatype_hints": ["HLAunicodeString"],
                    "lineage": ["TrackReport"],
                    "is_leaf": True,
                },
            ],
            "datatypes": ["AltitudeStruct", "EntityIdentifierStruct", "HLAunicodeString", "RTIobjectIdStruct"],
            "search_index": [
                {
                    "source_name": "demo",
                    "source_kind": "family",
                    "kind": "object",
                    "name": "HLAobjectRoot.BaseEntity",
                    "parent_name": "HLAobjectRoot",
                    "lineage": ["HLAobjectRoot.BaseEntity"],
                    "is_leaf": False,
                    "edition_classes": ["2010"],
                    "edition_scope": "2010 only",
                    "baseline_kinds": ["repo-owned"],
                    "load_mode": "standalone",
                },
                {
                    "source_name": "demo",
                    "source_kind": "family",
                    "kind": "object",
                    "name": "HLAobjectRoot.BaseEntity.PhysicalEntity.Platform.Aircraft",
                    "parent_name": "HLAobjectRoot.BaseEntity",
                    "lineage": [
                        "HLAobjectRoot.BaseEntity",
                        "HLAobjectRoot.BaseEntity.PhysicalEntity.Platform.Aircraft",
                    ],
                    "is_leaf": True,
                    "edition_classes": ["2010"],
                    "edition_scope": "2010 only",
                    "baseline_kinds": ["repo-owned"],
                    "load_mode": "standalone",
                },
                {
                    "source_name": "demo",
                    "source_kind": "family",
                    "kind": "interaction",
                    "name": "WeaponFire",
                    "parent_name": "HLAinteractionRoot",
                    "lineage": ["WeaponFire"],
                    "is_leaf": True,
                    "edition_classes": ["2010"],
                    "edition_scope": "2010 only",
                    "baseline_kinds": ["repo-owned"],
                    "load_mode": "standalone",
                },
                {
                    "source_name": "demo",
                    "source_kind": "family",
                    "kind": "datatype",
                    "name": "HLAunicodeString",
                    "parent_name": None,
                    "lineage": ["HLAunicodeString"],
                    "is_leaf": True,
                    "edition_classes": ["2010"],
                    "edition_scope": "2010 only",
                    "baseline_kinds": ["repo-owned"],
                    "load_mode": "standalone",
                },
            ],
        },
        "loaded_fom_set": {
            "record_ids": ["repo-2010-demo"],
            "member_paths": ["packages/hla-rti-core/src/hla/fom/resources/foms/DemoFOMmodule.xml"],
            "scenario_families": ["demo"],
            "edition_classes": ["2010"],
            "edition_scope": "2010 only",
            "baseline_kinds": ["repo-owned"],
            "load_modes": ["standalone"],
            "default_load_sets": [
                {
                    "scenario_family": "demo",
                    "member_ids": ["repo-2010-demo"],
                    "member_paths": ["packages/hla-rti-core/src/hla/fom/resources/foms/DemoFOMmodule.xml"],
                }
            ],
            "workbench_targets": [
                {
                    "label": "Open demo in workbench",
                    "target_kind": "family",
                    "target_name": "demo",
                    "fragment": "#family=demo",
                }
            ],
        },
        "history_event_count": 8,
    }


def _capture_workbench(page: Any, output_dir: Path) -> list[dict[str, str]]:
    workbench_dir = output_dir / "fom_workbench"
    html_path = write_fom_workbench_html(
        output_dir=workbench_dir,
        custom_load_sets={
            "custom-target-plus-demo": ("repo-cross-target-radar", "repo-2010-demo"),
        },
        diff_specs=(("target-radar", "custom-target-plus-demo"),),
    )
    captures: list[dict[str, str]] = []
    page.set_viewport_size({"width": 1680, "height": 1280})
    page.goto(html_path.resolve().as_uri())
    page.locator("#family-list .family-card").first.click()
    overview_path = output_dir / "workbench-overview.png"
    page.screenshot(path=str(overview_path), full_page=True)
    captures.append(
        {
            "title": "FOM Workbench Overview",
            "description": "Catalog, selection summary, and overview workspace for the hydrated workbench packet.",
            "image_rel": overview_path.name,
            "source": str(html_path.relative_to(output_dir)),
        }
    )
    page.click('.workspace-tab[data-workspace="diff"]')
    diff_path = output_dir / "workbench-diff.png"
    page.locator("#diff-panel").screenshot(path=str(diff_path))
    captures.append(
        {
            "title": "FOM Workbench Diff Panel",
            "description": "Pairwise family/load-set comparison panel for the hydrated workbench packet.",
            "image_rel": diff_path.name,
            "source": str(html_path.relative_to(output_dir)),
        }
    )
    page.click('.workspace-tab[data-workspace="validation"]')
    validation_path = output_dir / "workbench-validation.png"
    page.locator("#validation-panel").screenshot(path=str(validation_path))
    captures.append(
        {
            "title": "FOM Workbench Validation Panel",
            "description": "Validation-focused panel view for quick issue and command inspection.",
            "image_rel": validation_path.name,
            "source": str(html_path.relative_to(output_dir)),
        }
    )
    return captures


def _capture_visualizer(page: Any, output_dir: Path) -> list[dict[str, str]]:
    control = _StaticObserverControl(_demo_runtime_observer_state())
    app = create_runtime_observer_fastapi_app(control)
    captures: list[dict[str, str]] = []
    with run_local_app(app) as base_url:
        page.set_viewport_size({"width": 1720, "height": 1320})
        page.goto(base_url)
        page.wait_for_selector("#fom-detail")
        overview_path = output_dir / "visualizer-overview.png"
        page.screenshot(path=str(overview_path), full_page=True)
        captures.append(
            {
                "title": "Federation Visualizer Overview",
                "description": "Hydrated federation visualizer page with roster, events, object panels, and semantic overlays.",
                "image_rel": overview_path.name,
                "source": f"{base_url}/",
            }
        )
        page.locator("#objects-list .list-row[data-index]").first.click()
        object_pin_path = output_dir / "visualizer-object-pin.png"
        page.locator("#object-detail").screenshot(path=str(object_pin_path))
        captures.append(
            {
                "title": "Federation Visualizer Object Pin",
                "description": "Object detail after reciprocal pinning back into the FOM class state.",
                "image_rel": object_pin_path.name,
                "source": f"{base_url}/",
            }
        )
        page.locator("#fom-detail .tree-toggle-button").first.click()
        fom_panel_path = output_dir / "visualizer-fom-panel.png"
        page.locator("#fom-detail").screenshot(path=str(fom_panel_path))
        captures.append(
            {
                "title": "Federation Visualizer FOM Tree",
                "description": "Expanded FOM tree with direct and rollup runtime activity counts plus preview summaries.",
                "image_rel": fom_panel_path.name,
                "source": f"{base_url}/",
            }
        )
        plugin_path = output_dir / "visualizer-plugin-panel.png"
        page.locator("#plugin-root").screenshot(path=str(plugin_path))
        captures.append(
            {
                "title": "Federation Visualizer Semantic Panel",
                "description": "Hydrated semantic plugin panel for scenario-specific runtime summaries.",
                "image_rel": plugin_path.name,
                "source": f"{base_url}/",
            }
        )
    return captures


def _capture_federate_service(page: Any, output_dir: Path) -> list[dict[str, str]]:
    app = create_federate_service_fastapi_app()
    captures: list[dict[str, str]] = []
    with run_local_app(app) as base_url:
        page.set_viewport_size({"width": 1600, "height": 1200})
        page.goto(f"{base_url}/docs")
        page.wait_for_load_state("networkidle")
        docs_path = output_dir / "federate-service-docs.png"
        page.screenshot(path=str(docs_path), full_page=True)
        captures.append(
            {
                "title": "Federate Service Contract Docs",
                "description": "Swagger-backed contract surface for the bounded HLA RTIambassador-named service bridge.",
                "image_rel": docs_path.name,
                "source": f"{base_url}/docs",
            }
        )
    return captures

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a deterministic browser screenshot packet for major FOM and HLA observer/service UI surfaces.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=SCRIPT_REPO_ROOT / "artifacts" / "ui_surface_screenshots",
        help="Directory for generated screenshots and the HTML index.",
    )
    parser.add_argument(
        "--live-visualizer-url",
        help="Optional already-running federation visualizer URL to capture alongside the seeded local surfaces.",
    )
    parser.add_argument(
        "--live-federate-service-url",
        help="Optional already-running federate-service base/docs URL to capture alongside the seeded local surfaces.",
    )
    parser.add_argument(
        "--live-only",
        action="store_true",
        help="Capture only the supplied live surfaces and skip the seeded local workbench/visualizer/federate-service packet.",
    )
    args = parser.parse_args(argv)
    if args.live_only and not (args.live_visualizer_url or args.live_federate_service_url):
        parser.error("--live-only requires --live-visualizer-url and/or --live-federate-service-url.")

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    pw, browser, browser_name = launch_browser()
    try:
        page = browser.new_page()
        captures: list[dict[str, str]] = []
        if not args.live_only:
            captures.extend(_capture_workbench(page, output_dir))
            captures.extend(_capture_visualizer(page, output_dir))
            captures.extend(_capture_federate_service(page, output_dir))
        if args.live_visualizer_url:
            captures.extend(capture_live_visualizer(page, output_dir, base_url=args.live_visualizer_url))
        if args.live_federate_service_url:
            captures.extend(capture_live_federate_service(page, output_dir, base_url=args.live_federate_service_url))
        index_path = write_gallery_index(output_dir, browser_name=browser_name, captures=captures)
    finally:
        browser.close()
        pw.stop()

    write_gallery_manifest(
        output_dir,
        browser_name=browser_name,
        captures=captures,
        index_path=index_path,
    )
    print(index_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
