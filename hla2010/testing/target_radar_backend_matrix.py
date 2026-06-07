"""Target/radar backend matrix runner and artifact writer."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..backends.base import BackendUnavailableError
from ..scenarios import make_target_radar_factory, target_radar_fom_path
from ..scenarios.target_radar import run_target_radar_scenario


@dataclass(frozen=True)
class TargetRadarBackendMatrixPaths:
    output_dir: Path
    summary_json: Path
    results_csv: Path
    report_markdown: Path
    summary_svg: Path


@dataclass(frozen=True)
class TargetRadarBackendResult:
    backend: str
    status: str
    reason: str | None
    backend_kinds: tuple[str, str] | None
    track_reports: int
    first_range_m: float | None
    last_range_m: float | None
    range_delta_m: float | None
    final_time_seconds: float | None
    track_ids: list[str]


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(_jsonable(key)): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "as_dict") and callable(value.as_dict):
        return _jsonable(value.as_dict())
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(getattr(value, key)) for key in value.__dataclass_fields__}
    return repr(value)


def _target_radar_backend_options(backend_options_by_kind: Mapping[str, Mapping[str, Any]] | None, kind: str) -> dict[str, Any]:
    options: dict[str, Any] = {}
    if backend_options_by_kind is None:
        return options
    for key, value in backend_options_by_kind.get(kind, {}).items():
        options[key] = value
    return options


def run_target_radar_backend_matrix(
    backends: Sequence[str],
    *,
    target_radar_steps: int = 4,
    dt: float = 1.0,
    backend_options_by_kind: Mapping[str, Mapping[str, Any]] | None = None,
    federation_name_prefix: str = "target-radar-backend",
) -> dict[str, Any]:
    results: list[TargetRadarBackendResult] = []
    for backend in backends:
        options = _target_radar_backend_options(backend_options_by_kind, backend)
        federation_name = f"{federation_name_prefix}-{backend.replace('/', '-')}"
        try:
            result = run_target_radar_scenario(
                make_target_radar_factory(backend, backend_options=options),
                federation_name=federation_name,
                steps=target_radar_steps,
                dt=dt,
            )
            track_reports = list(result.track_reports)
            first_range = track_reports[0].range_m if track_reports else None
            last_range = track_reports[-1].range_m if track_reports else None
            results.append(
                TargetRadarBackendResult(
                    backend=backend,
                    status="passed",
                    reason=None,
                    backend_kinds=tuple(result.backend_kinds),
                    track_reports=len(track_reports),
                    first_range_m=first_range,
                    last_range_m=last_range,
                    range_delta_m=(last_range - first_range) if first_range is not None and last_range is not None else None,
                    final_time_seconds=track_reports[-1].time_seconds if track_reports else None,
                    track_ids=[report.track_id for report in track_reports],
                )
            )
        except (BackendUnavailableError, ImportError, ModuleNotFoundError) as exc:
            results.append(
                TargetRadarBackendResult(
                    backend=backend,
                    status="skipped",
                    reason=str(exc),
                    backend_kinds=None,
                    track_reports=0,
                    first_range_m=None,
                    last_range_m=None,
                    range_delta_m=None,
                    final_time_seconds=None,
                    track_ids=[],
                )
            )
        except OSError as exc:
            results.append(
                TargetRadarBackendResult(
                    backend=backend,
                    status="skipped",
                    reason=str(exc),
                    backend_kinds=None,
                    track_reports=0,
                    first_range_m=None,
                    last_range_m=None,
                    range_delta_m=None,
                    final_time_seconds=None,
                    track_ids=[],
                )
            )
        except Exception as exc:
            results.append(
                TargetRadarBackendResult(
                    backend=backend,
                    status="failed",
                    reason=f"{type(exc).__name__}: {exc}",
                    backend_kinds=None,
                    track_reports=0,
                    first_range_m=None,
                    last_range_m=None,
                    range_delta_m=None,
                    final_time_seconds=None,
                    track_ids=[],
                )
            )

    passed = sum(1 for item in results if item.status == "passed")
    skipped = sum(1 for item in results if item.status == "skipped")
    failed = sum(1 for item in results if item.status == "failed")
    summary = {
        "suite_name": "target-radar-backend-matrix",
        "target_radar_fom": target_radar_fom_path(),
        "steps": target_radar_steps,
        "dt": dt,
        "passed": passed,
        "skipped": skipped,
        "failed": failed,
        "results": [_jsonable(result) for result in results],
    }
    return summary


def _write_results_csv(path: Path, summary: Mapping[str, Any]) -> Path:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "backend",
                "status",
                "reason",
                "track_reports",
                "first_range_m",
                "last_range_m",
                "range_delta_m",
                "final_time_seconds",
                "backend_kinds",
                "track_ids",
            ],
        )
        writer.writeheader()
        for result in summary["results"]:
            writer.writerow(
                {
                    "backend": result["backend"],
                    "status": result["status"],
                    "reason": result.get("reason") or "",
                    "track_reports": result["track_reports"],
                    "first_range_m": result.get("first_range_m") or "",
                    "last_range_m": result.get("last_range_m") or "",
                    "range_delta_m": result.get("range_delta_m") or "",
                    "final_time_seconds": result.get("final_time_seconds") or "",
                    "backend_kinds": json.dumps(result.get("backend_kinds"), sort_keys=True),
                    "track_ids": json.dumps(result.get("track_ids", []), sort_keys=True),
                }
            )
    return path


def _write_markdown(path: Path, summary: Mapping[str, Any], results_csv: Path) -> Path:
    lines = [
        "# Target/Radar Backend Matrix",
        "",
        f"- suite: `{summary['suite_name']}`",
        f"- target radar FOM: `{summary['target_radar_fom']}`",
        f"- steps: `{summary['steps']}`",
        f"- dt: `{summary['dt']}`",
        f"- passed: `{summary['passed']}`",
        f"- skipped: `{summary['skipped']}`",
        f"- failed: `{summary['failed']}`",
        "",
        "## Results",
        "",
        "| Backend | Status | Track reports | Final range (m) | Final time | Reason |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for result in summary["results"]:
        lines.append(
            f"| {result['backend']} | {result['status']} | {result['track_reports']} | "
            f"{result.get('last_range_m') or ''} | {result.get('final_time_seconds') or ''} | {result.get('reason') or ''} |"
        )
    lines.extend(
        [
            "",
            "## How To Re-run",
            "",
            f"`python scripts/run_target_radar_backend_matrix.py --output-dir {results_csv.parent}`",
            "",
            "If a backend is skipped or failed, the reason above should point to the missing runtime, jar, classpath, or loopback/socket configuration that needs to be fixed.",
        ]
    )
    path.write_text("\n".join(lines) + "\n")
    return path


def _write_summary_svg(path: Path, summary: Mapping[str, Any]) -> Path:
    results = list(summary["results"])
    width = 1280
    row_height = 52
    top = 96
    height = top + row_height * len(results) + 60
    max_tracks = max((int(item["track_reports"]) for item in results), default=1)
    status_colors = {"passed": "#2b9348", "skipped": "#8d99ae", "failed": "#d00000"}
    rows: list[str] = []
    for index, item in enumerate(results):
        y = top + index * row_height
        bar_width = 360 * int(item["track_reports"]) / max_tracks if max_tracks else 0
        color = status_colors.get(item["status"], "#495057")
        rows.append(
            f'<text x="40" y="{y + 16}" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#132238">{item["backend"]}</text>'
            f'<rect x="240" y="{y}" width="120" height="24" rx="8" fill="{color}" opacity="0.92" />'
            f'<text x="300" y="{y + 16}" text-anchor="middle" font-size="12" font-family="Helvetica, Arial, sans-serif" fill="#ffffff">{item["status"]}</text>'
            f'<rect x="390" y="{y + 2}" width="{bar_width:.1f}" height="20" rx="8" fill="#2f6fed" opacity="0.9" />'
            f'<text x="400" y="{y + 16}" font-size="12" font-family="Helvetica, Arial, sans-serif" fill="#132238">{item["track_reports"]} track reports</text>'
            f'<text x="790" y="{y + 16}" font-size="12" font-family="Helvetica, Arial, sans-serif" fill="#48607a">{item.get("reason") or ""}</text>'
        )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#f6f8fb" />
  <text x="40" y="42" font-size="28" font-family="Helvetica, Arial, sans-serif" fill="#132238">Target/Radar Backend Matrix</text>
  <text x="40" y="70" font-size="14" font-family="Helvetica, Arial, sans-serif" fill="#48607a">Status and track-report counts for each requested backend profile.</text>
  <text x="40" y="96" font-size="13" font-family="Helvetica, Arial, sans-serif" fill="#48607a">Backend</text>
  <text x="240" y="96" font-size="13" font-family="Helvetica, Arial, sans-serif" fill="#48607a">Status</text>
  <text x="390" y="96" font-size="13" font-family="Helvetica, Arial, sans-serif" fill="#48607a">Scenario output</text>
  {''.join(rows)}
</svg>
"""
    path.write_text(svg)
    return path


def write_target_radar_backend_matrix_artifacts(
    output_dir: Path | str,
    backends: Sequence[str],
    *,
    target_radar_steps: int = 4,
    dt: float = 1.0,
    backend_options_by_kind: Mapping[str, Mapping[str, Any]] | None = None,
) -> TargetRadarBackendMatrixPaths:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = run_target_radar_backend_matrix(
        backends,
        target_radar_steps=target_radar_steps,
        dt=dt,
        backend_options_by_kind=backend_options_by_kind,
    )
    paths = TargetRadarBackendMatrixPaths(
        output_dir=output_dir,
        summary_json=output_dir / "target_radar_backend_matrix_summary.json",
        results_csv=output_dir / "target_radar_backend_matrix_results.csv",
        report_markdown=output_dir / "target_radar_backend_matrix_report.md",
        summary_svg=output_dir / "target_radar_backend_matrix_summary.svg",
    )
    paths.summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    _write_results_csv(paths.results_csv, summary)
    _write_markdown(paths.report_markdown, summary, paths.results_csv)
    _write_summary_svg(paths.summary_svg, summary)
    return paths


__all__ = [
    "TargetRadarBackendMatrixPaths",
    "TargetRadarBackendResult",
    "run_target_radar_backend_matrix",
    "write_target_radar_backend_matrix_artifacts",
]
