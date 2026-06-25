"""Top-to-bottom audit for the high-value SISO corpus families."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from hla.verification.repo_internal.fom_corpus_classification import classify_edition_scope
from hla.verification.repo_internal.fom_inventory import default_load_set_records, inventory_records_by_family
from hla.verification.repo_internal.fom_roundtrip import build_fom_roundtrip, write_fom_roundtrip
from hla.verification.repo_internal.fom_stress import _stress_annotation
from hla.verification.repo_internal.fom_validate import build_fom_validation, write_fom_validation
from hla.verification.repo_internal.fom_workbench import build_fom_workbench_snapshot, write_fom_workbench_html, write_fom_workbench_snapshot


HIGH_VALUE_SISO_FAMILIES = (
    "siso-rpr-2.0",
    "siso-rpr-3.0",
    "siso-link-16",
    "siso-space-fom",
    "siso-standard-mim",
    "siso-u-fom",
)


@dataclass(frozen=True, slots=True)
class FOMSisoAuditFamilyResult:
    family: str
    edition: str
    edition_scope: str
    stress_lane: str
    intended_role: str
    runtime_scenario_shape: str | None
    expected_result: str
    member_count: int
    source_paths: tuple[str, ...]
    bucket: str
    validation_passed: bool
    validation_verdict: str
    validation_error: str | None
    roundtrip_passed: bool
    roundtrip_year: int
    roundtrip_error: str | None
    validation_json_path: str
    validation_md_path: str
    roundtrip_json_path: str
    roundtrip_md_path: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FOMSisoAuditReport:
    title: str
    workbench_snapshot_path: str
    workbench_html_path: str
    workbench_error: str | None
    bucket_counts: dict[str, int]
    family_results: tuple[FOMSisoAuditFamilyResult, ...]

    @property
    def passed(self) -> bool:
        return all(result.validation_passed and result.roundtrip_passed for result in self.family_results)

    def to_json(self) -> str:
        return json.dumps(
            {
                "title": self.title,
                "passed": self.passed,
                "workbench_snapshot_path": self.workbench_snapshot_path,
                "workbench_html_path": self.workbench_html_path,
                "workbench_error": self.workbench_error,
                "bucket_counts": self.bucket_counts,
                "family_results": [result.as_dict() for result in self.family_results],
            },
            indent=2,
            sort_keys=True,
        )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


def _family_year(records: tuple[Any, ...]) -> int:
    if not records:
        return 2010
    return 2025 if any(record.edition_class == "2025" for record in records) else 2010


def _classify_family_result(
    *,
    validation_passed: bool,
    validation_verdict: str,
    validation_error: str | None,
    roundtrip_passed: bool,
) -> str:
    if validation_passed and roundtrip_passed:
        return "validate-clean"
    if validation_passed and not roundtrip_passed:
        return "roundtrip-only-stress"
    if validation_error is not None or validation_verdict in {"parse-failed", "error"}:
        return "parse-fail-fast"
    return "quarantine/unblock-needed"


def build_fom_siso_audit(
    *,
    output_root: str | Path | None = None,
    strict_identification: bool = False,
    title: str = "High-Value SISO FOM Audit",
) -> FOMSisoAuditReport:
    root = Path(output_root) if output_root is not None else _repo_root() / "analysis" / "fom_siso_audit"
    root.mkdir(parents=True, exist_ok=True)
    validation_root = root / "validation"
    roundtrip_root = root / "roundtrip"
    workbench_root = root / "workbench"
    validation_root.mkdir(parents=True, exist_ok=True)
    roundtrip_root.mkdir(parents=True, exist_ok=True)
    workbench_root.mkdir(parents=True, exist_ok=True)

    available_families = inventory_records_by_family()
    family_results: list[FOMSisoAuditFamilyResult] = []
    custom_load_sets: dict[str, tuple[str, ...]] = {}

    for family in HIGH_VALUE_SISO_FAMILIES:
        records = available_families.get(family, ())
        if not records:
            continue
        records = default_load_set_records(records)
        year = _family_year(records)
        stress_lane, intended_role, runtime_scenario_shape, expected_result = _stress_annotation(
            family,
            str(getattr(records[0], "baseline_kind", "third-party")),
            str(getattr(records[0], "load_mode", "ordered-family")),
        )
        source_paths = tuple(record.path for record in records)
        member_ids = tuple(record.id for record in records)
        custom_load_sets[family] = member_ids

        validation_error: str | None = None
        roundtrip_error: str | None = None
        validation_output_dir = validation_root / family
        roundtrip_output_dir = roundtrip_root / family
        validation_report: Any | None = None
        try:
            validation_json_path, validation_md_path, validation_report = write_fom_validation(
                (),
                output_dir=validation_output_dir,
                families=(family,),
                edition="auto",
                strict_identification=strict_identification,
                title=f"{family} | FOM Validation",
            )
        except Exception as exc:  # pragma: no cover - exercised in integration runs
            validation_error = str(exc)
            validation_output_dir.mkdir(parents=True, exist_ok=True)
            validation_json_path = validation_output_dir / "fom_validation_report.json"
            validation_md_path = validation_output_dir / "fom_validation_report.md"
            validation_json_path.write_text(json.dumps({"error": validation_error}, indent=2) + "\n", encoding="utf-8")
            validation_md_path.write_text(
                f"# {family} | FOM Validation\n\nValidation error: {validation_error}\n",
                encoding="utf-8",
            )

        if validation_report is not None:
            family_validation_row = next(
                (row for row in validation_report.load_set_reports if row.kind == "family" and row.name == family),
                None,
            )
            validation_passed = all(row.passed for row in validation_report.source_reports) and all(
                row.passed for row in validation_report.load_set_reports
            )
            validation_verdict = (
                family_validation_row.verdict
                if family_validation_row is not None
                else (validation_report.source_reports[0].verdict if validation_report.source_reports else "parse-failed")
            )
        else:
            validation_passed = False
            validation_verdict = "error"

        try:
            roundtrip_json_path, roundtrip_md_path = write_fom_roundtrip(
                year,
                source_paths,
                output_dir=roundtrip_output_dir,
                include_standard_mim=False,
                title=f"{family} | FOM Round Trip",
            )
            roundtrip_report = build_fom_roundtrip(
                year,
                source_paths,
                include_standard_mim=False,
                title=f"{family} | FOM Round Trip",
            )
            roundtrip_passed = all(
                row.xml_roundtrip_ok
                and row.protobuf_file_roundtrip_ok
                and row.protobuf_url_roundtrip_ok
                and row.protobuf_compressed_roundtrip_ok
                for row in roundtrip_report.module_reports
            )
            roundtrip_year = roundtrip_report.year
        except Exception as exc:  # pragma: no cover - exercised in integration runs
            roundtrip_error = str(exc)
            roundtrip_output_dir.mkdir(parents=True, exist_ok=True)
            roundtrip_json_path = roundtrip_output_dir / f"fom-roundtrip-{year}.json"
            roundtrip_md_path = roundtrip_output_dir / f"fom-roundtrip-{year}.md"
            roundtrip_json_path.write_text(json.dumps({"error": roundtrip_error}, indent=2) + "\n", encoding="utf-8")
            roundtrip_md_path.write_text(
                f"# {family} | FOM Round Trip\n\nRound-trip error: {roundtrip_error}\n",
                encoding="utf-8",
            )
            roundtrip_passed = False
            roundtrip_year = year

        bucket = _classify_family_result(
            validation_passed=validation_passed,
            validation_verdict=validation_verdict,
            validation_error=validation_error,
            roundtrip_passed=roundtrip_passed,
        )
        edition_scope = classify_edition_scope(records[0])
        family_results.append(
            FOMSisoAuditFamilyResult(
                family=family,
                edition=str(year),
                edition_scope=edition_scope,
                stress_lane=stress_lane,
                intended_role=intended_role,
                runtime_scenario_shape=runtime_scenario_shape,
                expected_result=expected_result,
                member_count=len(records),
                source_paths=source_paths,
                bucket=bucket,
                validation_passed=validation_passed,
                validation_verdict=validation_verdict,
                validation_error=validation_error,
                roundtrip_passed=roundtrip_passed,
                roundtrip_year=roundtrip_year,
                roundtrip_error=roundtrip_error,
                validation_json_path=str(validation_json_path),
                validation_md_path=str(validation_md_path),
                roundtrip_json_path=str(roundtrip_json_path),
                roundtrip_md_path=str(roundtrip_md_path),
            )
        )

    workbench_error: str | None = None
    try:
        workbench_snapshot_path = write_fom_workbench_snapshot(output_dir=workbench_root, custom_load_sets=custom_load_sets)
        workbench_html_path = write_fom_workbench_html(output_dir=workbench_root, custom_load_sets=custom_load_sets)
    except Exception as exc:  # pragma: no cover - exercised in integration runs
        workbench_error = str(exc)
        workbench_root.mkdir(parents=True, exist_ok=True)
        workbench_snapshot_path = workbench_root / "fom_workbench_snapshot.json"
        workbench_html_path = workbench_root / "fom_workbench.html"
        workbench_snapshot_path.write_text(json.dumps({"error": workbench_error}, indent=2) + "\n", encoding="utf-8")
        workbench_html_path.write_text(f"<!doctype html><pre>{workbench_error}</pre>", encoding="utf-8")

    return FOMSisoAuditReport(
        title=title,
        workbench_snapshot_path=str(workbench_snapshot_path),
        workbench_html_path=str(workbench_html_path),
        workbench_error=workbench_error,
        bucket_counts={
            bucket: sum(1 for row in family_results if row.bucket == bucket)
            for bucket in (
                "validate-clean",
                "roundtrip-only-stress",
                "parse-fail-fast",
                "quarantine/unblock-needed",
            )
        },
        family_results=tuple(family_results),
    )


def render_fom_siso_audit_markdown(report: FOMSisoAuditReport) -> str:
    lines = [
        f"# {report.title}",
        "",
        f"Overall status: {'passed' if report.passed else 'failed'}",
        "",
        f"- workbench snapshot: `{report.workbench_snapshot_path}`",
        f"- workbench html: `{report.workbench_html_path}`",
        f"- workbench error: `{report.workbench_error or 'none'}`",
        "",
        "| Bucket | Count |",
        "| --- | ---: |",
    ]
    for bucket in ("validate-clean", "roundtrip-only-stress", "parse-fail-fast", "quarantine/unblock-needed"):
        lines.append(f"| `{bucket}` | `{report.bucket_counts.get(bucket, 0)}` |")

    lines.extend(
        [
            "",
        "| Family | Edition | Scope | Lane | Expected | Runtime Shape | Members | Bucket | Validation | Round Trip | Verdict |",
            "| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for row in report.family_results:
        lines.append(
            "| "
            + " | ".join(
                (
                    f"`{row.family}`",
                    f"`{row.edition}`",
                    f"`{row.edition_scope}`",
                    f"`{row.stress_lane}`",
                    f"`{row.expected_result}`",
                    f"`{row.runtime_scenario_shape or 'n/a'}`",
                    str(row.member_count),
                    f"`{row.bucket}`",
                    "`passed`" if row.validation_passed else "`failed`",
                    "`passed`" if row.roundtrip_passed else "`failed`",
                    f"`{row.validation_verdict}`",
                )
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def write_fom_siso_audit(
    output_root: str | Path | None = None,
    *,
    strict_identification: bool = False,
    title: str = "High-Value SISO FOM Audit",
) -> tuple[Path, Path, FOMSisoAuditReport]:
    root = Path(output_root) if output_root is not None else _repo_root() / "analysis" / "fom_siso_audit"
    root.mkdir(parents=True, exist_ok=True)
    report = build_fom_siso_audit(output_root=root, strict_identification=strict_identification, title=title)
    json_path = root / "fom_siso_audit.json"
    md_path = root / "fom_siso_audit.md"
    json_path.write_text(report.to_json() + "\n", encoding="utf-8")
    md_path.write_text(render_fom_siso_audit_markdown(report), encoding="utf-8")
    return json_path, md_path, report


__all__ = [
    "FOMSisoAuditFamilyResult",
    "FOMSisoAuditReport",
    "HIGH_VALUE_SISO_FAMILIES",
    "build_fom_siso_audit",
    "render_fom_siso_audit_markdown",
    "write_fom_siso_audit",
]
