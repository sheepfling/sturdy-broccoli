"""Manifest-driven launcher for selected SISO runtime showcase rows."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .siso_runtime_showcase import load_siso_runtime_showcase_manifest, run_siso_runtime_showcase_scenario


@dataclass(frozen=True)
class SisoRuntimeShowcaseLauncherPaths:
    output_dir: Path
    summary_json: Path
    results_csv: Path
    selected_manifest_json: Path
    listener_root: Path
    report_markdown: Path


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return repr(value)


def _select_rows(
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


def run_siso_runtime_showcase_launcher(
    *,
    manifest_path: str | Path | None = None,
    families: Sequence[str] | None = None,
    editions: Sequence[str] | None = None,
    topologies: Sequence[str] | None = None,
    scenarios: Sequence[str] | None = None,
    backend: str | None = None,
    listener_output_dir: str | Path | None = None,
) -> dict[str, Any]:
    manifest = load_siso_runtime_showcase_manifest(manifest_path)
    selected = _select_rows(
        manifest,
        families=families,
        editions=editions,
        topologies=topologies,
        scenarios=scenarios,
    )
    results = [
        run_siso_runtime_showcase_scenario(
            str(row["scenario"]),
            backend=backend,
            listener_output_dir=listener_output_dir,
        )
        for row in selected
    ]
    return {
        "suite_name": "siso-runtime-showcase-launcher",
        "manifest_path": str(manifest_path) if manifest_path is not None else None,
        "backend_override": backend,
        "selected_scenario_count": len(selected),
        "status": "lifecycle-green" if all(bool(row["execution_complete"]) for row in results) else "failed",
        "results": results,
        "selected_manifest": {
            "schema_version": str(manifest["schema_version"]),
            "scenario_count": len(selected),
            "scenarios": selected,
        },
    }


def _write_results_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> Path:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "scenario",
                "family",
                "runtime_edition",
                "topology",
                "federate_count",
                "source_packet",
                "status",
                "execution_complete",
                "discoveries",
                "reflections",
                "interactions",
                "key_outcome",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _jsonable(row.get(field, "")) for field in writer.fieldnames})
    return path


def _render_markdown(summary: Mapping[str, Any], paths: SisoRuntimeShowcaseLauncherPaths) -> str:
    lines = [
        "# SISO Runtime Showcase Launcher",
        "",
        f"- suite: `{summary['suite_name']}`",
        f"- status: `{summary['status']}`",
        f"- selected scenarios: `{summary['selected_scenario_count']}`",
        f"- manifest path: `{summary.get('manifest_path')}`",
        f"- backend override: `{summary.get('backend_override')}`",
        f"- summary json: `{paths.summary_json}`",
        f"- results csv: `{paths.results_csv}`",
        f"- selected manifest json: `{paths.selected_manifest_json}`",
        f"- listener root: `{paths.listener_root}`",
        "",
        "## Results",
        "",
        "| Scenario | Family | Edition | Topology | Status | Discoveries | Reflections | Interactions |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for row in summary["results"]:
        lines.append(
            "| "
            + " | ".join(
                (
                    str(row["scenario"]),
                    str(row["family"]),
                    str(row["runtime_edition"]),
                    str(row["topology"]),
                    str(row["status"]),
                    str(row.get("discoveries", 0)),
                    str(row.get("reflections", 0)),
                    str(row.get("interactions", 0)),
                )
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def write_siso_runtime_showcase_launcher_artifacts(
    output_dir: str | Path,
    *,
    manifest_path: str | Path | None = None,
    families: Sequence[str] | None = None,
    editions: Sequence[str] | None = None,
    topologies: Sequence[str] | None = None,
    scenarios: Sequence[str] | None = None,
    backend: str | None = None,
) -> SisoRuntimeShowcaseLauncherPaths:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = SisoRuntimeShowcaseLauncherPaths(
        output_dir=out,
        summary_json=out / "siso_runtime_showcase_launcher_summary.json",
        results_csv=out / "siso_runtime_showcase_launcher_results.csv",
        selected_manifest_json=out / "siso_runtime_showcase_launcher_manifest.json",
        listener_root=out / "listener",
        report_markdown=out / "siso_runtime_showcase_launcher_report.md",
    )
    summary = run_siso_runtime_showcase_launcher(
        manifest_path=manifest_path,
        families=families,
        editions=editions,
        topologies=topologies,
        scenarios=scenarios,
        backend=backend,
        listener_output_dir=paths.listener_root,
    )
    paths.summary_json.write_text(json.dumps(_jsonable(summary), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths.selected_manifest_json.write_text(
        json.dumps(_jsonable(summary["selected_manifest"]), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_results_csv(paths.results_csv, summary["results"])
    paths.report_markdown.write_text(_render_markdown(summary, paths), encoding="utf-8")
    return paths


__all__ = [
    "SisoRuntimeShowcaseLauncherPaths",
    "run_siso_runtime_showcase_launcher",
    "write_siso_runtime_showcase_launcher_artifacts",
]
