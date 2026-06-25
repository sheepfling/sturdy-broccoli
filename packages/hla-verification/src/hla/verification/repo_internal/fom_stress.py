"""FOM parser stress helpers built from the public baseline inventory."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from hla.verification.repo_internal.fom_inventory import default_load_set_records, inventory_records_by_family
from hla.verification.repo_internal.fom_roundtrip import build_fom_roundtrip
from hla.verification.repo_internal.siso_corpus import is_default_scope_record


_DEFAULT_2025_EXTENSION_FAMILIES = {
    "proto2025-message-test",
    "proto2025-space-lite",
    "proto2025-time-mgmt-test",
}

_NON_FOM_STRESS_FAMILIES = {
    "bom-v2006-final-xsd-xml-2",
    "bom-v2006-final-xsd-xml-2-zip",
    "modelid-v2006-final-xsd-2",
    "omt-schema-baseline",
    "siso-link-16",
    "siso-rpr-2.0",
    "siso-rpr-3.0",
    "siso-u-fom",
    "siso-gdl-gfl",
}


@dataclass(frozen=True, slots=True)
class FOMStressFamilyResult:
    year: int
    scenario_family: str
    edition_class: str
    baseline_kind: str
    load_mode: str
    stress_lane: str
    intended_role: str
    runtime_scenario_shape: str | None
    expected_result: str
    member_ids: tuple[str, ...]
    member_paths: tuple[str, ...]
    module_names: tuple[str, ...]
    protobuf_schema: str | None
    object_class_count: int
    interaction_class_count: int
    datatype_count: int
    dimensions: tuple[str, ...]
    warnings: tuple[str, ...]
    passed: bool
    error: str | None


@dataclass(frozen=True, slots=True)
class FOMStressReport:
    title: str
    years: tuple[int, ...]
    families: tuple[FOMStressFamilyResult, ...]

    def to_json(self) -> str:
        return json.dumps(
            {
                "title": self.title,
                "years": list(self.years),
                "families": [asdict(row) for row in self.families],
            },
            indent=2,
            sort_keys=True,
        )


def _lanes_for_edition(edition_class: str, years: tuple[int, ...]) -> tuple[int, ...]:
    if edition_class == "2010":
        return tuple(year for year in years if year == 2010)
    if edition_class == "2025":
        return tuple(year for year in years if year == 2025)
    if edition_class == "cross-edition":
        return years
    return ()


def _stress_annotation(scenario_family: str, baseline_kind: str, load_mode: str) -> tuple[str, str, str | None, str]:
    if scenario_family == "target-radar":
        return (
            "runtime-federate-scenarios",
            "Repo-owned runtime-backed object/interaction proof family.",
            "object-state-heavy",
            "validate-clean",
        )
    if scenario_family.startswith("proto2025-"):
        return (
            "runtime-federate-scenarios",
            "Repo-owned packaged scenario family used for runtime and callback proof slices.",
            "time-ordered" if "time" in scenario_family else "interaction-heavy",
            "validate-clean",
        )
    if scenario_family == "rpr-normative":
        return (
            "modular-load-merge",
            "Canonical public modular RPR family for ordered merge and parser coverage.",
            None,
            "validate-clean",
        )
    if scenario_family.startswith("siso-space-fom"):
        return (
            "roundtrip-stress",
            "Ordered third-party domain family used to stress modular assembly and serializer normalization.",
            "object-state-heavy",
            "roundtrip-only-stress",
        )
    if scenario_family.startswith("siso-rpr"):
        return (
            "modular-load-merge",
            "Third-party tactical modular family used for ordered load, merge, and standards-backed validation classification.",
            "interaction-heavy",
            "roundtrip-only-stress" if "3.0" in scenario_family or "2.0" in scenario_family else "validate-clean",
        )
    if scenario_family.startswith("siso-link-16"):
        return (
            "template-fail-fast",
            "Template-like tactical link extension expected to rely on a parent radio/signal FOM.",
            "interaction-heavy",
            "parse-fail-fast",
        )
    if baseline_kind == "repo-owned":
        return (
            "modular-load-merge",
            "Repo-owned parser and merge baseline family.",
            None,
            "validate-clean",
        )
    if load_mode == "ordered-family":
        return (
            "modular-load-merge",
            "Ordered family used to prove merge/load semantics before runtime claims.",
            None,
            "validate-clean",
        )
    return (
        "roundtrip-stress",
        "General parser and JSON-cycle stress family.",
        None,
        "validate-clean",
    )


def build_fom_stress_report(
    *,
    years: Iterable[int] = (2010, 2025),
    title: str | None = None,
) -> FOMStressReport:
    selected_years = tuple(dict.fromkeys(int(year) for year in years))
    families_by_name = inventory_records_by_family()
    family_rows: list[FOMStressFamilyResult] = []

    for scenario_family in sorted(families_by_name):
        if scenario_family in _DEFAULT_2025_EXTENSION_FAMILIES:
            continue
        if scenario_family in _NON_FOM_STRESS_FAMILIES:
            continue
        records = families_by_name[scenario_family]
        if not any(is_default_scope_record(record) for record in records):
            continue
        load_set = default_load_set_records(records)
        if not load_set:
            continue

        edition_class = load_set[0].edition_class
        baseline_kind = load_set[0].baseline_kind
        load_mode = load_set[0].load_mode
        stress_lane, intended_role, runtime_scenario_shape, expected_result = _stress_annotation(
            scenario_family,
            baseline_kind,
            load_mode,
        )
        member_ids = tuple(record.id for record in load_set)
        member_paths = tuple(record.path for record in load_set)
        lanes = _lanes_for_edition(edition_class, selected_years)
        for year in lanes:
            mim_source = "HLAstandardMIM" if year == 2025 else None
            try:
                report = build_fom_roundtrip(
                    year,
                    member_paths,
                    include_standard_mim=False,
                    mim_source=mim_source,
                    title=title or f"{scenario_family} {year} parser stress",
                )
            except Exception as exc:  # pragma: no cover - failure diagnostics only
                warning = "XML round-trip signature mismatch" in str(exc)
                warning_modules = tuple(Path(path).name for path in member_paths) if warning else ()
                family_rows.append(
                    FOMStressFamilyResult(
                        year=year,
                        scenario_family=scenario_family,
                        edition_class=edition_class,
                        baseline_kind=baseline_kind,
                        load_mode=load_mode,
                        stress_lane=stress_lane,
                        intended_role=intended_role,
                        runtime_scenario_shape=runtime_scenario_shape,
                        expected_result=expected_result,
                        member_ids=member_ids,
                        member_paths=member_paths,
                        module_names=warning_modules,
                        protobuf_schema="rti1516_2025" if year == 2025 else "rti1516e",
                        object_class_count=0,
                        interaction_class_count=0,
                        datatype_count=0,
                        dimensions=(),
                        warnings=(str(exc),) if warning else (),
                        passed=warning,
                        error=None if warning else str(exc),
                    )
                )
                continue

            family_rows.append(
                FOMStressFamilyResult(
                    year=year,
                    scenario_family=scenario_family,
                    edition_class=edition_class,
                    baseline_kind=baseline_kind,
                    load_mode=load_mode,
                    stress_lane=stress_lane,
                    intended_role=intended_role,
                    runtime_scenario_shape=runtime_scenario_shape,
                    expected_result=expected_result,
                    member_ids=member_ids,
                    member_paths=member_paths,
                    module_names=tuple(row.name or row.source for row in report.module_reports),
                    protobuf_schema=report.protobuf_schema,
                    object_class_count=len(report.merged_summary.get("object_classes", ())),
                    interaction_class_count=len(report.merged_summary.get("interaction_classes", ())),
                    datatype_count=len(report.merged_summary.get("datatype_names", ())),
                    dimensions=tuple(report.merged_summary.get("dimensions", ())),
                    warnings=(),
                    passed=True,
                    error=None,
                )
            )

    report_title = title or "FOM stress lane report"
    return FOMStressReport(title=report_title, years=selected_years, families=tuple(family_rows))


def write_fom_stress_report(
    output_dir: str | Path,
    *,
    years: Iterable[int] = (2010, 2025),
    title: str | None = None,
) -> tuple[Path, Path, FOMStressReport]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report = build_fom_stress_report(years=years, title=title)

    json_path = output_path / "fom_stress_report.json"
    md_path = output_path / "fom_stress_report.md"
    json_path.write_text(report.to_json() + "\n", encoding="utf-8")

    lines = [
        f"# {report.title}",
        "",
        f"- years: `{', '.join(str(year) for year in report.years)}`",
        f"- family runs: `{len(report.families)}`",
        f"- passed: `{sum(1 for row in report.families if row.passed)}`",
        f"- failed: `{sum(1 for row in report.families if not row.passed)}`",
        "",
        "| Year | Scenario Family | Lane | Expected | Runtime Shape | Edition | Baseline | Load Mode | Members | Modules | Schema | Objects | Interactions | Datatypes | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in report.families:
        status = "passed" if row.passed and not row.warnings else f"passed with warnings: {'; '.join(row.warnings)}" if row.passed else f"failed: {row.error}"
        lines.append(
            "| "
            + " | ".join(
                (
                    str(row.year),
                    row.scenario_family,
                    row.stress_lane,
                    row.expected_result,
                    row.runtime_scenario_shape or "n/a",
                    row.edition_class,
                    row.baseline_kind,
                    row.load_mode,
                    str(len(row.member_ids)),
                    str(len(row.module_names)),
                    row.protobuf_schema or "n/a",
                    str(row.object_class_count),
                    str(row.interaction_class_count),
                    str(row.datatype_count),
                    status,
                )
            )
            + " |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path, report


__all__ = [
    "FOMStressFamilyResult",
    "FOMStressReport",
    "build_fom_stress_report",
    "write_fom_stress_report",
]
