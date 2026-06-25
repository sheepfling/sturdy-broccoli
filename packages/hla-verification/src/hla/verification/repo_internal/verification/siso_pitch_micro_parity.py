"""Pitch-only micro-scenario parity packet for the SISO runtime showcase."""
from __future__ import annotations

import csv
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from hla.backends.common import BackendUnavailableError

from .siso_runtime_showcase import (
    build_siso_runtime_showcase_manifest,
    run_siso_runtime_showcase_scenario,
)
from .two_federate_runtime_launchers import build_two_federate_runtime_launchers


@dataclass(frozen=True)
class SisoPitchMicroParityPaths:
    output_dir: Path
    summary_json: Path
    results_csv: Path
    selected_manifest_json: Path
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


def _close_resource(resource: Any | None) -> None:
    if resource is None:
        return
    close = getattr(resource, "close", None)
    if callable(close):
        try:
            close()
        except BaseException:
            pass
    terminate = getattr(resource, "terminate", None)
    if callable(terminate):
        try:
            terminate()
        except BaseException:
            pass


def _micro_vendor_rows() -> list[dict[str, Any]]:
    manifest = build_siso_runtime_showcase_manifest()
    rows: list[dict[str, Any]] = []
    for row in manifest["scenarios"]:
        if int(row["federate_count"]) != 2:
            continue
        profiles = list(row["pitch_2010_profiles"]) + list(row["pitch_202x_profiles"])
        if not profiles:
            continue
        for backend in profiles:
            rows.append(
                {
                    "scenario": row["scenario"],
                    "family": row["family"],
                    "runtime_edition": row["runtime_edition"],
                    "topology": row["topology"],
                    "federate_count": row["federate_count"],
                    "source_packet": row["source_packet"],
                    "backend": backend,
                    "counts_as_vendor_runtime": backend in {"pitch-jpype", "pitch-py4j"},
                    "vendor_notes": row["vendor_notes"],
                }
            )
    return rows


def _pitch_preflight_confirmed() -> bool:
    if os.environ.get("HLA2010_PITCH_PREFLIGHT_OK") == "1":
        return True
    artifact_dir = Path(os.environ.get("HLA2010_PREFLIGHT_ARTIFACT_DIR", "artifacts/preflight_artifacts"))
    path = artifact_dir / "pitch-preflight.json"
    if not path.exists():
        return False
    max_age_seconds = float(os.environ.get("HLA2010_PREFLIGHT_MAX_AGE_SECONDS", "43200"))
    try:
        if max_age_seconds > 0 and (time.time() - path.stat().st_mtime) > max_age_seconds:
            return False
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        str(payload.get("tool", "")) == "pitch-preflight"
        and int(payload.get("exit_code", 1)) == 0
        and str(payload.get("environment", "")) == "ready"
        and str(payload.get("result", "")) == "ready to run ./tools/pitch install or ./tools/pitch all"
    )


def run_siso_pitch_micro_parity(
    *,
    backends: Sequence[str] | None = None,
    require_real_vendor_preflight: bool = False,
    real_vendor_only: bool = False,
) -> dict[str, Any]:
    launcher_by_backend = build_two_federate_runtime_launchers()
    requested = set(backends or ())
    selected_rows = [
        row for row in _micro_vendor_rows() if not requested or row["backend"] in requested
    ]
    if real_vendor_only:
        selected_rows = [row for row in selected_rows if bool(row["counts_as_vendor_runtime"])]
    if require_real_vendor_preflight and not _pitch_preflight_confirmed():
        raise RuntimeError("Pitch preflight not confirmed; run `./tools/pitch preflight` before the strict micro lane.")
    results: list[dict[str, Any]] = []
    for row in selected_rows:
        runtime_resource = None
        try:
            if bool(row["counts_as_vendor_runtime"]) and not require_real_vendor_preflight and os.environ.get("HLA2010_ENABLE_REAL_RTI_SMOKE") != "1":
                results.append(
                    {
                        **row,
                        "status": "skipped",
                        "reason": "real Pitch vendor runtime disabled; set HLA2010_ENABLE_REAL_RTI_SMOKE=1",
                        "execution_complete": False,
                        "discoveries": 0,
                        "reflections": 0,
                        "interactions": 0,
                        "lifecycle": [],
                    }
                )
                continue
            launcher = launcher_by_backend.get(str(row["backend"]))
            if launcher is not None:
                runtime_resource = launcher()
            scenario_result = run_siso_runtime_showcase_scenario(str(row["scenario"]), backend=str(row["backend"]))
            results.append(
                {
                    **row,
                    "status": "passed" if bool(scenario_result["execution_complete"]) else "failed",
                    "reason": None if bool(scenario_result["execution_complete"]) else "scenario execution incomplete",
                    "execution_complete": bool(scenario_result["execution_complete"]),
                    "discoveries": int(scenario_result.get("discoveries", 0)),
                    "reflections": int(scenario_result.get("reflections", 0)),
                    "interactions": int(scenario_result.get("interactions", 0)),
                    "lifecycle": list(scenario_result.get("lifecycle", [])),
                    "operation_attempts": _jsonable(scenario_result.get("operation_attempts", {})),
                    "federate_callback_summaries": _jsonable(scenario_result.get("federate_callback_summaries", {})),
                    "delivered_tags": _jsonable(scenario_result.get("delivered_tags", [])),
                }
            )
        except (BackendUnavailableError, ModuleNotFoundError, ImportError, OSError) as exc:
            results.append(
                {
                    **row,
                    "status": "skipped",
                    "reason": str(exc),
                    "execution_complete": False,
                    "discoveries": 0,
                    "reflections": 0,
                    "interactions": 0,
                    "lifecycle": [],
                }
            )
        except Exception as exc:
            results.append(
                {
                    **row,
                    "status": "failed",
                    "reason": f"{type(exc).__name__}: {exc}",
                    "execution_complete": False,
                    "discoveries": 0,
                    "reflections": 0,
                    "interactions": 0,
                    "lifecycle": [],
                }
            )
        finally:
            _close_resource(runtime_resource)

    return {
        "suite_name": "siso-pitch-micro-parity",
        "scope": "Pitch-eligible SISO micro-2 scenarios only.",
        "strict_real_vendor_preflight": require_real_vendor_preflight,
        "real_vendor_only": real_vendor_only,
        "selected_scenario_count": len(selected_rows),
        "passed": sum(1 for row in results if row["status"] == "passed"),
        "skipped": sum(1 for row in results if row["status"] == "skipped"),
        "failed": sum(1 for row in results if row["status"] == "failed"),
        "results": results,
        "selected_manifest": {
            "schema_version": "siso-pitch-micro-parity-v0.1",
            "scenario_count": len(selected_rows),
            "rows": selected_rows,
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
                "backend",
                "counts_as_vendor_runtime",
                "status",
                "reason",
                "execution_complete",
                "discoveries",
                "reflections",
                "interactions",
                "vendor_notes",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _jsonable(row.get(key, "")) for key in writer.fieldnames})
    return path


def _render_markdown(summary: Mapping[str, Any], paths: SisoPitchMicroParityPaths) -> str:
    lines = [
        "# SISO Pitch Micro Parity",
        "",
        f"- suite: `{summary['suite_name']}`",
        f"- scope: `{summary['scope']}`",
        f"- selected scenarios: `{summary['selected_scenario_count']}`",
        f"- passed: `{summary['passed']}`",
        f"- skipped: `{summary['skipped']}`",
        f"- failed: `{summary['failed']}`",
        f"- summary json: `{paths.summary_json}`",
        f"- results csv: `{paths.results_csv}`",
        f"- selected manifest json: `{paths.selected_manifest_json}`",
        "",
        "## Results",
        "",
        "| Scenario | Backend | Edition | Family | Status | Discoveries | Reflections | Interactions | Vendor Runtime | Reason |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in summary["results"]:
        lines.append(
            "| "
            + " | ".join(
                (
                    str(row["scenario"]),
                    str(row["backend"]),
                    str(row["runtime_edition"]),
                    str(row["family"]),
                    str(row["status"]),
                    str(row["discoveries"]),
                    str(row["reflections"]),
                    str(row["interactions"]),
                    "yes" if bool(row["counts_as_vendor_runtime"]) else "bounded-no",
                    str(row.get("reason") or ""),
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- `pitch-jpype` and `pitch-py4j` count as real 2010 vendor-runtime rows.",
            "- `pitch-202x-jpype` and `pitch-202x-py4j` are bounded adapter rows over the repo Python 2025 runtime and do not count as IEEE 1516.1-2025 vendor conformance.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_siso_pitch_micro_parity_artifacts(
    output_dir: str | Path,
    *,
    backends: Sequence[str] | None = None,
    require_real_vendor_preflight: bool = False,
    real_vendor_only: bool = False,
) -> SisoPitchMicroParityPaths:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = SisoPitchMicroParityPaths(
        output_dir=out,
        summary_json=out / "siso_pitch_micro_parity_summary.json",
        results_csv=out / "siso_pitch_micro_parity_results.csv",
        selected_manifest_json=out / "siso_pitch_micro_parity_manifest.json",
        report_markdown=out / "siso_pitch_micro_parity_report.md",
    )
    summary = run_siso_pitch_micro_parity(
        backends=backends,
        require_real_vendor_preflight=require_real_vendor_preflight,
        real_vendor_only=real_vendor_only,
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
    "SisoPitchMicroParityPaths",
    "run_siso_pitch_micro_parity",
    "write_siso_pitch_micro_parity_artifacts",
]
