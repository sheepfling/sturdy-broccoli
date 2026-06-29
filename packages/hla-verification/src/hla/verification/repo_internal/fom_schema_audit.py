"""Top-to-bottom audit for the schema-positive FOM cases."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from hla.verification.repo_internal.fom_roundtrip import build_fom_roundtrip, write_fom_roundtrip
from hla.verification.repo_internal.fom_schema_baseline import (
    FOMSchemaBaselineCase,
    load_fom_schema_baseline_cases,
)
from hla.verification.repo_internal.fom_validate import write_fom_validation
from hla.verification.repo_internal.fom_workbench import write_fom_workbench_html, write_fom_workbench_snapshot


@dataclass(frozen=True, slots=True)
class FOMSchemaAuditCaseResult:
    id: str
    edition: str
    xml_path: str
    schema_path: str
    purpose: str
    validation_passed: bool
    validation_verdict: str
    roundtrip_passed: bool
    roundtrip_year: int
    validation_json_path: str
    validation_md_path: str
    roundtrip_json_path: str
    roundtrip_md_path: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FOMSchemaAuditReport:
    title: str
    workbench_snapshot_path: str
    workbench_html_path: str
    case_results: tuple[FOMSchemaAuditCaseResult, ...]

    @property
    def passed(self) -> bool:
        return all(result.validation_passed and result.roundtrip_passed for result in self.case_results)

    def to_json(self) -> str:
        return json.dumps(
            {
                "title": self.title,
                "passed": self.passed,
                "workbench_snapshot_path": self.workbench_snapshot_path,
                "workbench_html_path": self.workbench_html_path,
                "case_results": [result.as_dict() for result in self.case_results],
            },
            indent=2,
            sort_keys=True,
        )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


def _case_ids(cases: tuple[FOMSchemaBaselineCase, ...]) -> tuple[str, ...]:
    return tuple(case.inventory_id or case.id for case in cases)


def build_fom_schema_audit(
    *,
    output_root: str | Path | None = None,
    strict_identification: bool = False,
    title: str = "FOM Schema Top-to-Bottom Audit",
) -> FOMSchemaAuditReport:
    root = Path(output_root) if output_root is not None else _repo_root() / "analysis" / "fom_schema_audit"
    root.mkdir(parents=True, exist_ok=True)
    cases = load_fom_schema_baseline_cases(repo_root=_repo_root())
    validation_root = root / "validation"
    roundtrip_root = root / "roundtrip"
    workbench_root = root / "workbench"
    validation_root.mkdir(parents=True, exist_ok=True)
    roundtrip_root.mkdir(parents=True, exist_ok=True)
    workbench_root.mkdir(parents=True, exist_ok=True)

    results: list[FOMSchemaAuditCaseResult] = []
    for case in cases:
        validation_json_path, validation_md_path, validation_report = write_fom_validation(
            [case.xml_path],
            output_dir=validation_root / case.id,
            edition=case.edition,  # type: ignore[arg-type]
            schema_path=case.schema_path,
            strict_identification=strict_identification,
            title=f"{case.id} | FOM Validation",
        )
        roundtrip_json_path, roundtrip_md_path = write_fom_roundtrip(
            int(case.edition),
            [case.xml_path],
            output_dir=roundtrip_root / case.id,
            include_standard_mim=False,
            title=f"{case.id} | FOM Round Trip",
        )
        roundtrip_report = build_fom_roundtrip(
            int(case.edition),
            [case.xml_path],
            include_standard_mim=False,
            title=f"{case.id} | FOM Round Trip",
        )
        validation_row = validation_report.source_reports[0]
        results.append(
            FOMSchemaAuditCaseResult(
                id=case.id,
                edition=case.edition,
                xml_path=case.xml_path,
                schema_path=case.schema_path,
                purpose=case.purpose,
                validation_passed=validation_row.passed,
                validation_verdict=validation_row.verdict,
                roundtrip_passed=all(row.xml_roundtrip_ok and row.protobuf_file_roundtrip_ok and row.protobuf_url_roundtrip_ok and row.protobuf_compressed_roundtrip_ok for row in roundtrip_report.module_reports),
                roundtrip_year=roundtrip_report.year,
                validation_json_path=str(validation_json_path),
                validation_md_path=str(validation_md_path),
                roundtrip_json_path=str(roundtrip_json_path),
                roundtrip_md_path=str(roundtrip_md_path),
            )
        )

    custom_load_sets = {"schema-baseline": _case_ids(cases)}
    workbench_snapshot_path = write_fom_workbench_snapshot(output_dir=workbench_root, custom_load_sets=custom_load_sets)
    workbench_html_path = write_fom_workbench_html(output_dir=workbench_root, custom_load_sets=custom_load_sets)

    return FOMSchemaAuditReport(
        title=title,
        workbench_snapshot_path=str(workbench_snapshot_path),
        workbench_html_path=str(workbench_html_path),
        case_results=tuple(results),
    )


def render_fom_schema_audit_markdown(report: FOMSchemaAuditReport) -> str:
    lines = [
        f"# {report.title}",
        "",
        f"Overall status: {'passed' if report.passed else 'failed'}",
        "",
        f"- workbench snapshot: `{report.workbench_snapshot_path}`",
        f"- workbench html: `{report.workbench_html_path}`",
        "",
        "| Case | Validation | Round Trip | Validation Verdict | XML | Schema |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.case_results:
        lines.append(
            "| "
            + " | ".join(
                (
                    f"`{row.id}`",
                    "`passed`" if row.validation_passed else "`failed`",
                    "`passed`" if row.roundtrip_passed else "`failed`",
                    f"`{row.validation_verdict}`",
                    row.xml_path,
                    row.schema_path,
                )
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def write_fom_schema_audit(
    output_root: str | Path | None = None,
    *,
    strict_identification: bool = False,
    title: str = "FOM Schema Top-to-Bottom Audit",
) -> tuple[Path, Path, FOMSchemaAuditReport]:
    root = Path(output_root) if output_root is not None else _repo_root() / "analysis" / "fom_schema_audit"
    root.mkdir(parents=True, exist_ok=True)
    report = build_fom_schema_audit(output_root=root, strict_identification=strict_identification, title=title)
    json_path = root / "fom_schema_audit.json"
    md_path = root / "fom_schema_audit.md"
    json_path.write_text(report.to_json() + "\n", encoding="utf-8")
    md_path.write_text(render_fom_schema_audit_markdown(report), encoding="utf-8")
    return json_path, md_path, report


__all__ = [
    "FOMSchemaAuditCaseResult",
    "FOMSchemaAuditReport",
    "build_fom_schema_audit",
    "render_fom_schema_audit_markdown",
    "write_fom_schema_audit",
]
