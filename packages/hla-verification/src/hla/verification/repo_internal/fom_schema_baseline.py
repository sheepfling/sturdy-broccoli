"""Dedicated schema-validation baseline helpers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from hla.fom.validation import ValidationIssue, validate_omt_xml_schema


@dataclass(frozen=True, slots=True)
class FOMSchemaBaselineCase:
    id: str
    inventory_id: str | None
    edition: str
    xml_path: str
    schema_path: str
    purpose: str


@dataclass(frozen=True, slots=True)
class FOMSchemaBaselineCaseResult:
    id: str
    edition: str
    xml_path: str
    schema_path: str
    purpose: str
    passed: bool
    issue_count: int
    issues: tuple[ValidationIssue, ...]

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["issues"] = [
            {
                "requirement": issue.requirement,
                "table": issue.table,
                "field": issue.field,
                "value": issue.value,
                "status": issue.status,
                "message": issue.message,
            }
            for issue in self.issues
        ]
        return payload


@dataclass(frozen=True, slots=True)
class FOMSchemaBaselineReport:
    title: str
    case_results: tuple[FOMSchemaBaselineCaseResult, ...]

    @property
    def passed(self) -> bool:
        return all(result.passed for result in self.case_results)

    def to_json(self) -> str:
        return json.dumps(
            {
                "title": self.title,
                "passed": self.passed,
                "case_results": [result.as_dict() for result in self.case_results],
            },
            indent=2,
            sort_keys=True,
        )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


def _manifest_path(repo_root: Path | None = None) -> Path:
    base_root = repo_root if repo_root is not None else _repo_root()
    return base_root / "third_party" / "fom_schema_baseline" / "manifest" / "schema_baseline_sources.json"


def _load_cases(repo_root: Path | None = None) -> tuple[FOMSchemaBaselineCase, ...]:
    manifest = json.loads(_manifest_path(repo_root).read_text(encoding="utf-8"))
    return tuple(FOMSchemaBaselineCase(**entry) for entry in manifest["cases"])


def load_fom_schema_baseline_cases(*, repo_root: Path | None = None) -> tuple[FOMSchemaBaselineCase, ...]:
    return _load_cases(repo_root)


def build_fom_schema_baseline(
    *,
    repo_root: Path | None = None,
    title: str = "FOM Schema Validation Baseline",
) -> FOMSchemaBaselineReport:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    results: list[FOMSchemaBaselineCaseResult] = []
    for case in _load_cases(root):
        xml_path = root / case.xml_path
        schema_path = root / case.schema_path
        issues = tuple(validate_omt_xml_schema(xml_path, schema_path))
        results.append(
            FOMSchemaBaselineCaseResult(
                id=case.id,
                edition=case.edition,
                xml_path=case.xml_path,
                schema_path=case.schema_path,
                purpose=case.purpose,
                passed=not issues,
                issue_count=len(issues),
                issues=issues,
            )
        )
    return FOMSchemaBaselineReport(title=title, case_results=tuple(results))


def render_fom_schema_baseline_markdown(report: FOMSchemaBaselineReport) -> str:
    lines = [
        f"# {report.title}",
        "",
        "Positive schema-validation baseline for the XML validation lane.",
        "",
        f"Overall status: {'passed' if report.passed else 'failed'}",
        "",
        "| Case | Edition | XML | Schema | Result | Issues | Purpose |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in report.case_results:
        lines.append(
            "| "
            + " | ".join(
                (
                    f"`{result.id}`",
                    f"`{result.edition}`",
                    result.xml_path,
                    result.schema_path,
                    "`passed`" if result.passed else "`failed`",
                    f"`{result.issue_count}`",
                    result.purpose,
                )
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def write_fom_schema_baseline(
    output_root: str | Path | None = None,
    *,
    repo_root: Path | None = None,
    title: str = "FOM Schema Validation Baseline",
) -> tuple[Path, Path, FOMSchemaBaselineReport]:
    root = Path(output_root) if output_root is not None else _repo_root() / "analysis" / "fom_schema_baseline"
    root.mkdir(parents=True, exist_ok=True)
    report = build_fom_schema_baseline(repo_root=repo_root, title=title)
    json_path = root / "fom_schema_baseline.json"
    md_path = root / "fom_schema_baseline.md"
    json_path.write_text(report.to_json() + "\n", encoding="utf-8")
    md_path.write_text(render_fom_schema_baseline_markdown(report), encoding="utf-8")
    return json_path, md_path, report


__all__ = [
    "FOMSchemaBaselineCase",
    "FOMSchemaBaselineCaseResult",
    "FOMSchemaBaselineReport",
    "build_fom_schema_baseline",
    "load_fom_schema_baseline_cases",
    "render_fom_schema_baseline_markdown",
    "write_fom_schema_baseline",
]
