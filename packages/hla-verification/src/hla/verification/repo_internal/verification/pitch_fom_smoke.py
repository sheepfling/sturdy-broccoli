"""Artifact-backed Pitch example-FOM smoke coverage."""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any

from hla.backends.common import RecordingFederateAmbassador
from hla.runtime.factory import create_rti_ambassador
from hla.runtime.rti1516_2025_factory import create_rti_ambassador as create_rti_ambassador_2025
from hla.rti1516e.enums import ResignAction
from hla.rti1516_2025.enums import ResignAction as ResignAction2025
from hla.verification.repo_internal.fom_inventory import inventory_records
from hla.verification.startup import FederationStartupConfig, connect_create_join


@dataclass(frozen=True)
class PitchFomSmokeSpec:
    id: str
    scenario_family: str
    load_mode: str
    notes: str
    fom_modules: tuple[str, ...]
    object_class_name: str
    interaction_class_name: str


@dataclass(frozen=True)
class PitchFomSmokePaths:
    output_dir: Path
    summary_json: Path
    report_markdown: Path


@dataclass(frozen=True)
class PitchFomRuntimeProfile:
    kind: str
    spec_name: str
    evidence_mode: str
    counts_as_vendor_runtime: bool


_RUNTIME_PROFILES: dict[str, PitchFomRuntimeProfile] = {
    "pitch-jpype": PitchFomRuntimeProfile(
        kind="pitch-jpype",
        spec_name="rti1516e",
        evidence_mode="vendor-runtime",
        counts_as_vendor_runtime=True,
    ),
    "pitch-py4j": PitchFomRuntimeProfile(
        kind="pitch-py4j",
        spec_name="rti1516e",
        evidence_mode="vendor-runtime",
        counts_as_vendor_runtime=True,
    ),
    "pitch-202x-jpype": PitchFomRuntimeProfile(
        kind="pitch-202x-jpype",
        spec_name="rti1516_2025",
        evidence_mode="adapter-backed",
        counts_as_vendor_runtime=False,
    ),
    "pitch-202x-py4j": PitchFomRuntimeProfile(
        kind="pitch-202x-py4j",
        spec_name="rti1516_2025",
        evidence_mode="adapter-backed",
        counts_as_vendor_runtime=False,
    ),
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[7]


def _call_service(target: Any, snake_name: str, camel_name: str, *args: Any) -> Any:
    method = getattr(target, snake_name, None) or getattr(target, camel_name)
    return method(*args)


def launch_pitch_runtime() -> Any:
    launcher = import_module("hla.vendors.pitch.real_rti_pitch").launch_pitch_runtime
    return launcher()


def _inventory_path(record_id: str) -> str:
    repo_root = _repo_root()
    for record in inventory_records():
        if record.id == record_id:
            return str((repo_root / record.path).resolve())
    raise KeyError(f"Unknown FOM inventory record {record_id!r}")


def build_default_pitch_fom_smoke_specs() -> tuple[PitchFomSmokeSpec, ...]:
    return (
        PitchFomSmokeSpec(
            id="repo-2010-demo",
            scenario_family="demo",
            load_mode="standalone",
            notes="Small bundled 2010 demo surface to prove baseline create/join/lookup behavior.",
            fom_modules=(_inventory_path("repo-2010-demo"),),
            object_class_name="HLAobjectRoot.DemoObject",
            interaction_class_name="HLAinteractionRoot.Ping",
        ),
        PitchFomSmokeSpec(
            id="repo-cross-target-radar",
            scenario_family="target-radar",
            load_mode="standalone",
            notes="Cross-edition repo-owned target/radar baseline used heavily by the shared verification ladders.",
            fom_modules=(_inventory_path("repo-cross-target-radar"),),
            object_class_name="HLAobjectRoot.Target",
            interaction_class_name="HLAinteractionRoot.TrackReport",
        ),
        PitchFomSmokeSpec(
            id="link16-rpr2-integrated",
            scenario_family="siso-rpr-2.0",
            load_mode="ordered-family",
            notes="Link 16 plus RPR 2.0 integrated family; stresses ordered-family load composition.",
            fom_modules=tuple(str(path) for path in _resolve_packet_paths("link16-rpr2-integrated")),
            object_class_name="HLAobjectRoot.EmbeddedSystem.RadioTransmitter",
            interaction_class_name="HLAinteractionRoot.RadioSignal.RawBinaryRadioSignal.TDLBinaryRadioSignal.Link16RadioSignal.JTIDSMessageRadioSignal",
        ),
        PitchFomSmokeSpec(
            id="rpr3-merged-informative-1516-2010",
            scenario_family="siso-rpr-3.0",
            load_mode="ordered-family",
            notes="Datatype-heavy RPR 3.0 merged packet with variant records, arrays, and tactical interaction families.",
            fom_modules=tuple(str(path) for path in _resolve_packet_paths("rpr3-merged-informative-1516-2010")),
            object_class_name="HLAobjectRoot.EnvironmentObject.PointObject.BridgeObject",
            interaction_class_name="HLAinteractionRoot.Fire.WeaponFire",
        ),
        PitchFomSmokeSpec(
            id="space-fom-core",
            scenario_family="siso-space-fom",
            load_mode="ordered-family",
            notes="Space FOM ordered-family baseline with deeper datatype and hierarchy breadth than the repo-owned demo fixtures.",
            fom_modules=tuple(str(path) for path in _resolve_packet_paths("space-fom-core")),
            object_class_name="HLAobjectRoot.ReferenceFrame",
            interaction_class_name="HLAinteractionRoot.ReferenceFrameAnnouncement",
        ),
    )


def _resolve_packet_paths(packet_id: str) -> tuple[str, ...]:
    from .siso_runtime_showcase import _packet_paths

    return tuple(_packet_paths(packet_id))


def _cleanup_runtime_case(rti: Any | None, runtime: Any | None, federation_name: str) -> None:
    if rti is not None:
        try:
            resign_action = (
                ResignAction2025.DELETE_OBJECTS
                if getattr(getattr(rti, "backend_info", None), "details", {}).get("spec") == "rti1516_2025"
                else ResignAction.DELETE_OBJECTS
            )
            _call_service(rti, "resign_federation_execution", "resignFederationExecution", resign_action)
        except Exception:
            pass
        try:
            _call_service(rti, "destroy_federation_execution", "destroyFederationExecution", federation_name)
        except Exception:
            pass
        try:
            _call_service(rti, "disconnect", "disconnect")
        except Exception:
            pass
        try:
            close = getattr(rti, "close", None)
            if close is not None:
                close()
        except Exception:
            pass
    if runtime is not None:
        try:
            close = getattr(runtime, "close", None)
            if close is not None:
                close()
        except Exception:
            pass


def probe_pitch_fom_support(
    *,
    runtime_kinds: tuple[str, ...] = ("pitch-jpype", "pitch-py4j"),
    specs: tuple[PitchFomSmokeSpec, ...] | None = None,
) -> dict[str, Any]:
    selected_specs = specs or build_default_pitch_fom_smoke_specs()
    rows: list[dict[str, Any]] = []
    for kind in runtime_kinds:
        profile = _RUNTIME_PROFILES[kind]
        runtime = launch_pitch_runtime() if profile.counts_as_vendor_runtime else None
        try:
            for spec in selected_specs:
                federation_name = f"pitch-fom-{kind}-{spec.id}-{uuid.uuid4().hex[:8]}"
                rti = None
                try:
                    if profile.spec_name == "rti1516_2025":
                        rti = create_rti_ambassador_2025(backend=kind)
                    else:
                        rti = create_rti_ambassador(kind)
                    startup = connect_create_join(
                        rti,
                        RecordingFederateAmbassador(),
                        FederationStartupConfig(
                            federation_name=federation_name,
                            federate_name=f"{kind}-{spec.id}",
                            federate_type="PitchFomProbe",
                            fom_modules=tuple(spec.fom_modules),
                            logical_time_implementation_name="HLAinteger64Time",
                            ready_to_run_sync_point=None,
                        ),
                    )
                    object_handle = _call_service(
                        rti, "get_object_class_handle", "getObjectClassHandle", spec.object_class_name
                    )
                    interaction_handle = _call_service(
                        rti, "get_interaction_class_handle", "getInteractionClassHandle", spec.interaction_class_name
                    )
                    rows.append(
                        {
                            "runtime_kind": kind,
                            "spec_name": profile.spec_name,
                            "evidence_mode": profile.evidence_mode,
                            "counts_as_vendor_runtime": profile.counts_as_vendor_runtime,
                            "packet_id": spec.id,
                            "scenario_family": spec.scenario_family,
                            "load_mode": spec.load_mode,
                            "status": "lookup-green",
                            "federation_name": federation_name,
                            "fom_modules": list(spec.fom_modules),
                            "object_class_name": spec.object_class_name,
                            "interaction_class_name": spec.interaction_class_name,
                            "object_handle_repr": repr(object_handle),
                            "interaction_handle_repr": repr(interaction_handle),
                            "created_federation": bool(startup.created_federation),
                            "notes": spec.notes,
                        }
                    )
                except Exception as exc:
                    rows.append(
                        {
                            "runtime_kind": kind,
                            "spec_name": profile.spec_name,
                            "evidence_mode": profile.evidence_mode,
                            "counts_as_vendor_runtime": profile.counts_as_vendor_runtime,
                            "packet_id": spec.id,
                            "scenario_family": spec.scenario_family,
                            "load_mode": spec.load_mode,
                            "status": "failed",
                            "federation_name": federation_name,
                            "fom_modules": list(spec.fom_modules),
                            "object_class_name": spec.object_class_name,
                            "interaction_class_name": spec.interaction_class_name,
                            "error_type": type(exc).__name__,
                            "error_message": str(exc),
                            "notes": spec.notes,
                        }
                    )
                finally:
                    _cleanup_runtime_case(rti, None, federation_name)
        finally:
            _cleanup_runtime_case(None, runtime, "")
    success_count = sum(1 for row in rows if row["status"] == "lookup-green")
    failure_count = len(rows) - success_count
    by_runtime: dict[str, dict[str, int]] = {}
    for row in rows:
        runtime_bucket = by_runtime.setdefault(row["runtime_kind"], {"lookup_green": 0, "failed": 0})
        if row["status"] == "lookup-green":
            runtime_bucket["lookup_green"] += 1
        else:
            runtime_bucket["failed"] += 1
    return {
        "suite_name": "pitch-fom-smoke",
        "packet_count": len(selected_specs),
        "runtime_count": len(runtime_kinds),
        "row_count": len(rows),
        "runtime_profiles": [
            {
                "kind": profile.kind,
                "spec_name": profile.spec_name,
                "evidence_mode": profile.evidence_mode,
                "counts_as_vendor_runtime": profile.counts_as_vendor_runtime,
            }
            for profile in (_RUNTIME_PROFILES[kind] for kind in runtime_kinds)
        ],
        "lookup_green_count": success_count,
        "failed_count": failure_count,
        "by_runtime": by_runtime,
        "rows": rows,
    }


def render_pitch_fom_smoke_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Pitch FOM Smoke",
        "",
        f"- packet count: `{summary['packet_count']}`",
        f"- runtime count: `{summary['runtime_count']}`",
        f"- row count: `{summary['row_count']}`",
        f"- lookup green count: `{summary['lookup_green_count']}`",
        f"- failed count: `{summary['failed_count']}`",
        "",
        "## Runtime Profiles",
        "",
        "| Runtime | Spec | Evidence mode | Counts as vendor runtime |",
        "| --- | --- | --- | --- |",
    ]
    for profile in summary.get("runtime_profiles", []):
        lines.append(
            f"| {profile['kind']} | {profile['spec_name']} | {profile['evidence_mode']} | {profile['counts_as_vendor_runtime']} |"
        )
    lines.extend(
        [
            "",
            "> `adapter-backed` rows exercise the checked-in `pitch-202x-*` wrappers over the repo Python 2025 backend. They do not prove native Pitch vendor-runtime behavior.",
            "",
            "| Runtime | Packet | Family | Mode | Evidence | Status | Notes |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in summary["rows"]:
        lines.append(
            f"| {row['runtime_kind']} | {row['packet_id']} | {row['scenario_family']} | {row['load_mode']} | "
            f"{row['evidence_mode']} | {row['status']} | {row['notes']} |"
        )
    lines.append("")
    lines.append("## Failures")
    lines.append("")
    failures = [row for row in summary["rows"] if row["status"] != "lookup-green"]
    if not failures:
        lines.append("- none")
    else:
        for row in failures:
            lines.append(
                f"- `{row['runtime_kind']} / {row['packet_id']}`: `{row.get('error_type', 'unknown')}` {row.get('error_message', '')}".rstrip()
            )
    return "\n".join(lines) + "\n"


def write_pitch_fom_smoke(output_dir: Path | str, summary: dict[str, Any]) -> PitchFomSmokePaths:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    paths = PitchFomSmokePaths(
        output_dir=output_path,
        summary_json=output_path / "pitch_fom_smoke_summary.json",
        report_markdown=output_path / "pitch_fom_smoke_report.md",
    )
    paths.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths.report_markdown.write_text(render_pitch_fom_smoke_markdown(summary), encoding="utf-8")
    return paths


__all__ = [
    "PitchFomSmokePaths",
    "PitchFomSmokeSpec",
    "build_default_pitch_fom_smoke_specs",
    "probe_pitch_fom_support",
    "render_pitch_fom_smoke_markdown",
    "write_pitch_fom_smoke",
]
