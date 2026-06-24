"""Artifact-backed showcase scenarios for the high-value SISO FOM families."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from hla.verification.repo_internal.fom_corpus_classification import classify_edition_scope
from hla.verification.repo_internal.fom_inventory import (
    FOMInventoryRecord,
    default_load_set_for_family,
    inventory_records,
)
from hla.verification.repo_internal.fom_overview import build_fom_overview, write_fom_overview, write_fom_overview_html
from hla.verification.repo_internal.fom_roundtrip import build_fom_roundtrip, write_fom_roundtrip
from hla.verification.repo_internal.fom_validate import write_fom_validation, write_fom_validation_html
from hla.verification.repo_internal.fom_workbench import write_fom_workbench_html, write_fom_workbench_snapshot


@dataclass(frozen=True, slots=True)
class ShowcasePacketSpec:
    id: str
    title: str
    showcase_id: str
    showcase_title: str
    year: int
    expected_buckets: tuple[str, ...]
    summary: str
    family: str | None = None
    member_ids: tuple[str, ...] = ()
    include_path_fragments: tuple[str, ...] = ()
    exclude_path_fragments: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ShowcaseGroupSpec:
    id: str
    title: str
    summary: str
    packet_ids: tuple[str, ...]
    event_ladder: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FOMSisoShowcasePacketResult:
    id: str
    title: str
    showcase_id: str
    showcase_title: str
    summary: str
    year: int
    edition_scope: str
    member_ids: tuple[str, ...]
    source_paths: tuple[str, ...]
    expected_buckets: tuple[str, ...]
    bucket: str
    matches_expectation: bool
    validation_passed: bool
    validation_verdict: str
    validation_error: str | None
    roundtrip_passed: bool
    roundtrip_error: str | None
    overview_passed: bool
    overview_error: str | None
    object_class_count: int
    interaction_class_count: int
    datatype_count: int
    dimensions: tuple[str, ...]
    feature_highlights: tuple[str, ...]
    validation_json_path: str
    validation_md_path: str
    validation_html_path: str | None
    roundtrip_json_path: str
    roundtrip_md_path: str
    overview_json_path: str | None
    overview_md_path: str | None
    overview_html_path: str | None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FOMSisoShowcaseReport:
    title: str
    packet_results: tuple[FOMSisoShowcasePacketResult, ...]
    workbench_snapshot_path: str
    workbench_html_path: str
    workbench_error: str | None
    bucket_counts: dict[str, int]

    @property
    def passed(self) -> bool:
        return self.workbench_error is None and all(result.matches_expectation for result in self.packet_results)

    def to_json(self) -> str:
        payload = {
            "title": self.title,
            "passed": self.passed,
            "workbench_snapshot_path": self.workbench_snapshot_path,
            "workbench_html_path": self.workbench_html_path,
            "workbench_error": self.workbench_error,
            "bucket_counts": self.bucket_counts,
            "showcases": [asdict(group) for group in _SHOWCASE_GROUPS],
            "packet_results": [row.as_dict() for row in self.packet_results],
        }
        return json.dumps(payload, indent=2, sort_keys=True)


_PACKET_SPECS = (
    ShowcasePacketSpec(
        id="link16-standalone-template",
        title="Link 16 standalone template",
        showcase_id="link16",
        showcase_title="Link 16 Showcase",
        year=2010,
        expected_buckets=("parse-fail-fast",),
        summary="Standalone Link 16 is a deliberate fail-fast template: it exposes hierarchy and parent-integration assumptions immediately.",
        member_ids=("siso-siso-link-16-link-16-v2-0",),
    ),
    ShowcasePacketSpec(
        id="link16-rpr2-integrated",
        title="Link 16 integrated through RPR 2.0",
        showcase_id="link16",
        showcase_title="Link 16 Showcase",
        year=2010,
        expected_buckets=("validate-clean", "roundtrip-only-stress"),
        summary="The integrated RPR 2.0 package turns Link 16 into a concrete tactical-link load set with parent hierarchy, radio semantics, and merged enumerations.",
        family="siso-rpr-2.0",
        include_path_fragments=("RPR FOM v2.0 Link 16 and Link 11",),
    ),
    ShowcasePacketSpec(
        id="rpr3-annex-a-normative",
        title="RPR 3.0 Annex A normative family",
        showcase_id="rpr3",
        showcase_title="RPR 3.0 Showcase",
        year=2025,
        expected_buckets=("validate-clean", "parse-fail-fast"),
        summary="This is the main clean tactical federation showcase: the current normative RPR pack, ordered and merged as intended.",
        family="siso-rpr-3.0",
        include_path_fragments=("Annex A Files Normative",),
        exclude_path_fragments=("Annex B Files Informative",),
    ),
    ShowcasePacketSpec(
        id="rpr3-merged-informative-1516-2010",
        title="RPR 3.0 informative merged 1516-2010 packet",
        showcase_id="rpr3",
        showcase_title="RPR 3.0 Showcase",
        year=2025,
        expected_buckets=("roundtrip-only-stress",),
        summary="This is the scale-stress companion packet: one large merged RPR 3.0 XML that is useful for parser, JSON-cycle, and visualizer load.",
        member_ids=("siso-siso-rpr-3-0-rpr-fom-v3-0-1516-2010",),
    ),
    ShowcasePacketSpec(
        id="space-fom-core",
        title="Space FOM ordered core family",
        showcase_id="space",
        showcase_title="Space FOM Showcase",
        year=2010,
        expected_buckets=("roundtrip-only-stress", "validate-clean"),
        summary="The Space FOM ordered family broadens the ontology: environment, entity, management, and orbital-state datatypes all merge in one packet.",
        family="siso-space-fom",
    ),
)

_SHOWCASE_GROUPS = (
    ShowcaseGroupSpec(
        id="link16",
        title="Link 16 Showcase",
        summary="Show the transition from a template-like tactical-link module to an integrated tactical communication load set.",
        packet_ids=("link16-standalone-template", "link16-rpr2-integrated"),
        event_ladder=(
            "Template check: the standalone Link 16 XML fails fast because the object hierarchy begins at RadioTransmitter rather than HLAobjectRoot.",
            "Envelope publish: TDLBinaryRadioSignal establishes the tactical-link radio-signal container.",
            "Link context: Link16RadioSignal adds NPG number, net number, crypto labels, Link 16 version, and time-slot identity.",
            "Message traffic: JTIDSMessageRadioSignal carries TADIL-J words for the common tactical message path.",
            "Timing closure: RTTABRadioSignal and RTTReplyRadioSignal exercise request/reply timing flows.",
            "Payload diversity: voice, LET, and VMF leaves stress variable payload shapes inside one interaction family.",
        ),
    ),
    ShowcaseGroupSpec(
        id="rpr3",
        title="RPR 3.0 Showcase",
        summary="Show the current tactical federation pack in both normative ordered-family form and giant merged stress-packet form.",
        packet_ids=("rpr3-annex-a-normative", "rpr3-merged-informative-1516-2010"),
        event_ladder=(
            "Platform state: PhysicalEntity and AggregateEntity establish the tactical operating picture.",
            "Comms surface: the communication modules add radio, transmitter, and signal payload structures to the battlefield model.",
            "Weapon release: the Fire interaction starts an engagement with munition identity and launch context.",
            "Battle effect: Detonation closes the engagement chain with result coding and detonation state.",
            "Operational breadth: logistics, SE, IO, and SIMAN modules deepen sustainment and side-effect coverage beyond a small demo FOM.",
            "Scale stress: the merged informative packet shifts the emphasis from semantics to raw parser, JSON-cycle, and visualizer pressure.",
        ),
    ),
    ShowcaseGroupSpec(
        id="space",
        title="Space FOM Showcase",
        summary="Show a broader domain model with orbital-state datatypes, environment concerns, and ordered family assembly pressure.",
        packet_ids=("space-fom-core",),
        event_ladder=(
            "Environment baseline: the environment module establishes the global context that mission entities share.",
            "Entity publication: PhysicalEntity and related space entities enter the federation with domain-specific state.",
            "State vector updates: SpaceTimeCoordinateState and AttitudeQuaternion stress compound orbital-state datatypes.",
            "Management coordination: the management module adds federation-facing control and lifecycle semantics around the domain entities.",
            "Ordered assembly: the family demonstrates why datatypes, switches, management, environment, and entity modules must merge in sequence.",
        ),
    ),
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


def _inventory_by_id() -> dict[str, FOMInventoryRecord]:
    return {record.id: record for record in inventory_records()}


def _resolve_packet_records(spec: ShowcasePacketSpec) -> tuple[FOMInventoryRecord, ...]:
    if spec.family is not None:
        records = default_load_set_for_family(spec.family)
    else:
        by_id = _inventory_by_id()
        records = tuple(by_id[member_id] for member_id in spec.member_ids)
    filtered: list[FOMInventoryRecord] = []
    seen_paths: set[str] = set()
    for record in records:
        path_text = record.path
        if spec.include_path_fragments and not all(fragment in path_text for fragment in spec.include_path_fragments):
            continue
        if spec.exclude_path_fragments and any(fragment in path_text for fragment in spec.exclude_path_fragments):
            continue
        if path_text in seen_paths:
            continue
        seen_paths.add(path_text)
        filtered.append(record)
    if filtered:
        return tuple(filtered)
    return records


def _records_scope(records: tuple[FOMInventoryRecord, ...]) -> str:
    scopes = {classify_edition_scope(record) for record in records}
    if not scopes:
        return "schema-only / support-only"
    if len(scopes) == 1:
        return next(iter(scopes))
    return "cross-edition / ambiguous"


def _classify_bucket(
    *,
    validation_passed: bool,
    validation_verdict: str,
    validation_error: str | None,
    roundtrip_passed: bool,
    roundtrip_error: str | None,
    overview_error: str | None,
) -> str:
    if validation_passed and roundtrip_passed:
        return "validate-clean"
    if roundtrip_passed and overview_error is None and not validation_passed:
        return "roundtrip-only-stress"
    if validation_verdict == "conforming" and overview_error is None and roundtrip_error is not None:
        return "roundtrip-only-stress"
    if validation_passed and not roundtrip_passed:
        return "roundtrip-only-stress"
    if roundtrip_error is not None or overview_error is not None:
        return "parse-fail-fast"
    if validation_error is not None or validation_verdict in {"parse-failed", "error"}:
        return "parse-fail-fast"
    return "quarantine/unblock-needed"


def _leaf_rows(rows: tuple[Any, ...]) -> tuple[Any, ...]:
    parent_names = {row.parent_name for row in rows if row.parent_name}
    leaves = [row for row in rows if row.full_name not in parent_names]
    return tuple(leaves or rows)


def _highlight_rows(rows: tuple[Any, ...], *, limit: int) -> tuple[str, ...]:
    highlights: list[str] = []
    for row in _leaf_rows(rows):
        member_count = row.total_count
        if member_count == 0:
            continue
        label = f"{row.full_name} ({member_count} members)"
        if label not in highlights:
            highlights.append(label)
        if len(highlights) >= limit:
            break
    return tuple(highlights)


def _feature_highlights(overview_report: Any | None) -> tuple[str, ...]:
    if overview_report is None:
        return ()
    highlights = [
        f"{len(overview_report.object_rows)} object classes",
        f"{len(overview_report.interaction_rows)} interaction classes",
        f"{len(overview_report.merged_summary.get('datatype_names', ())) if isinstance(overview_report.merged_summary.get('datatype_names'), (list, tuple, set)) else len(overview_report.dimensions)} dimensions-ready summary",
    ]
    for label in _highlight_rows(overview_report.interaction_rows, limit=4):
        highlights.append(f"interaction leaf: {label}")
    for label in _highlight_rows(overview_report.object_rows, limit=3):
        highlights.append(f"object leaf: {label}")
    if overview_report.dimensions:
        highlights.append(f"dimensions: {', '.join(overview_report.dimensions[:4])}")
    return tuple(dict.fromkeys(highlights))


def build_fom_siso_showcase(
    *,
    output_root: str | Path | None = None,
    packet_ids: tuple[str, ...] | None = None,
    strict_identification: bool = False,
    title: str = "High-Value SISO FOM Showcase",
) -> FOMSisoShowcaseReport:
    root = Path(output_root) if output_root is not None else _repo_root() / "analysis" / "fom_siso_showcase"
    root.mkdir(parents=True, exist_ok=True)
    validation_root = root / "validation"
    roundtrip_root = root / "roundtrip"
    overview_root = root / "overview"
    workbench_root = root / "workbench"
    validation_root.mkdir(parents=True, exist_ok=True)
    roundtrip_root.mkdir(parents=True, exist_ok=True)
    overview_root.mkdir(parents=True, exist_ok=True)
    workbench_root.mkdir(parents=True, exist_ok=True)

    selected_specs = tuple(spec for spec in _PACKET_SPECS if packet_ids is None or spec.id in packet_ids)
    packet_results: list[FOMSisoShowcasePacketResult] = []
    custom_load_sets: dict[str, tuple[str, ...]] = {}

    for spec in selected_specs:
        records = _resolve_packet_records(spec)
        member_ids = tuple(record.id for record in records)
        custom_load_sets[spec.id] = member_ids
        source_paths = tuple(str(_repo_root() / record.path) for record in records)
        edition_scope = _records_scope(records)

        validation_output_dir = validation_root / spec.id
        roundtrip_output_dir = roundtrip_root / spec.id
        overview_output_dir = overview_root / spec.id

        validation_error: str | None = None
        roundtrip_error: str | None = None
        overview_error: str | None = None
        validation_html_path: str | None = None
        overview_json_path: str | None = None
        overview_md_path: str | None = None
        overview_html_path: str | None = None
        overview_report: Any | None = None

        try:
            validation_json_path, validation_md_path, validation_report = write_fom_validation(
                source_paths,
                output_dir=validation_output_dir,
                edition=str(spec.year),
                strict_identification=strict_identification,
                title=f"{spec.title} | FOM Validation",
            )
            validation_html = write_fom_validation_html(
                source_paths,
                output_dir=validation_output_dir,
                edition=str(spec.year),
                strict_identification=strict_identification,
                title=f"{spec.title} | FOM Validation",
            )
            validation_html_path = str(validation_html)
            validation_passed = all(row.passed for row in validation_report.source_reports) and all(
                row.passed for row in validation_report.load_set_reports
            )
            validation_verdict = (
                validation_report.load_set_reports[0].verdict
                if validation_report.load_set_reports
                else (validation_report.source_reports[0].verdict if validation_report.source_reports else "parse-failed")
            )
        except Exception as exc:  # pragma: no cover - integration failure path
            validation_error = str(exc)
            validation_output_dir.mkdir(parents=True, exist_ok=True)
            validation_json = validation_output_dir / "fom_validation_report.json"
            validation_md = validation_output_dir / "fom_validation_report.md"
            validation_json.write_text(json.dumps({"error": validation_error}, indent=2) + "\n", encoding="utf-8")
            validation_md.write_text(f"# {spec.title} | FOM Validation\n\nValidation error: {validation_error}\n", encoding="utf-8")
            validation_json_path = validation_json
            validation_md_path = validation_md
            validation_passed = False
            validation_verdict = "error"

        try:
            roundtrip_json_path, roundtrip_md_path = write_fom_roundtrip(
                spec.year,
                source_paths,
                output_dir=roundtrip_output_dir,
                include_standard_mim=False,
                title=f"{spec.title} | FOM Round Trip",
            )
            roundtrip_report = build_fom_roundtrip(
                spec.year,
                source_paths,
                include_standard_mim=False,
                title=f"{spec.title} | FOM Round Trip",
            )
            roundtrip_passed = all(
                row.xml_roundtrip_ok
                and row.protobuf_file_roundtrip_ok
                and row.protobuf_url_roundtrip_ok
                and row.protobuf_compressed_roundtrip_ok
                for row in roundtrip_report.module_reports
            )
        except Exception as exc:  # pragma: no cover - integration failure path
            roundtrip_error = str(exc)
            roundtrip_output_dir.mkdir(parents=True, exist_ok=True)
            roundtrip_json = roundtrip_output_dir / f"fom-roundtrip-{spec.year}.json"
            roundtrip_md = roundtrip_output_dir / f"fom-roundtrip-{spec.year}.md"
            roundtrip_json.write_text(json.dumps({"error": roundtrip_error}, indent=2) + "\n", encoding="utf-8")
            roundtrip_md.write_text(f"# {spec.title} | FOM Round Trip\n\nRound-trip error: {roundtrip_error}\n", encoding="utf-8")
            roundtrip_json_path = roundtrip_json
            roundtrip_md_path = roundtrip_md
            roundtrip_passed = False

        object_count = 0
        interaction_count = 0
        datatype_count = 0
        dimensions: tuple[str, ...] = ()
        try:
            overview_json, overview_md = write_fom_overview(
                source_paths,
                output_dir=overview_output_dir,
                include_standard_mim=False,
                title=f"{spec.title} | FOM Overview",
            )
            overview_html = write_fom_overview_html(
                source_paths,
                output_dir=overview_output_dir,
                include_standard_mim=False,
                title=f"{spec.title} | FOM Overview",
            )
            overview_report = build_fom_overview(
                source_paths,
                include_standard_mim=False,
                title=f"{spec.title} | FOM Overview",
            )
            overview_json_path = str(overview_json)
            overview_md_path = str(overview_md)
            overview_html_path = str(overview_html)
            object_count = len(overview_report.object_rows)
            interaction_count = len(overview_report.interaction_rows)
            datatype_count = len(tuple(overview_report.merged_summary.get("datatype_names", ())))
            dimensions = tuple(overview_report.dimensions)
            overview_passed = True
        except Exception as exc:  # pragma: no cover - integration failure path
            overview_error = str(exc)
            overview_passed = False

        bucket = _classify_bucket(
            validation_passed=validation_passed,
            validation_verdict=validation_verdict,
            validation_error=validation_error,
            roundtrip_passed=roundtrip_passed,
            roundtrip_error=roundtrip_error,
            overview_error=overview_error,
        )
        packet_results.append(
            FOMSisoShowcasePacketResult(
                id=spec.id,
                title=spec.title,
                showcase_id=spec.showcase_id,
                showcase_title=spec.showcase_title,
                summary=spec.summary,
                year=spec.year,
                edition_scope=edition_scope,
                member_ids=member_ids,
                source_paths=source_paths,
                expected_buckets=spec.expected_buckets,
                bucket=bucket,
                matches_expectation=bucket in spec.expected_buckets,
                validation_passed=validation_passed,
                validation_verdict=validation_verdict,
                validation_error=validation_error,
                roundtrip_passed=roundtrip_passed,
                roundtrip_error=roundtrip_error,
                overview_passed=overview_passed,
                overview_error=overview_error,
                object_class_count=object_count,
                interaction_class_count=interaction_count,
                datatype_count=datatype_count,
                dimensions=dimensions,
                feature_highlights=_feature_highlights(overview_report),
                validation_json_path=str(validation_json_path),
                validation_md_path=str(validation_md_path),
                validation_html_path=validation_html_path,
                roundtrip_json_path=str(roundtrip_json_path),
                roundtrip_md_path=str(roundtrip_md_path),
                overview_json_path=overview_json_path,
                overview_md_path=overview_md_path,
                overview_html_path=overview_html_path,
            )
        )

    diff_specs: tuple[tuple[str, str], ...] = tuple(
        tuple(spec.split(":", 1))  # type: ignore[arg-type]
        for spec in (
            "link16-rpr2-integrated:rpr3-annex-a-normative",
            "rpr3-annex-a-normative:space-fom-core",
        )
        if all(part in custom_load_sets for part in spec.split(":", 1))
    )
    workbench_error: str | None = None
    try:
        workbench_snapshot_path = str(
            write_fom_workbench_snapshot(output_dir=workbench_root, custom_load_sets=custom_load_sets, diff_specs=diff_specs)
        )
        workbench_html_path = str(
            write_fom_workbench_html(output_dir=workbench_root, custom_load_sets=custom_load_sets, diff_specs=diff_specs)
        )
    except Exception as exc:  # pragma: no cover - integration failure path
        workbench_error = str(exc)
        snapshot_path = workbench_root / "fom_workbench_snapshot.json"
        html_path = workbench_root / "fom_workbench.html"
        snapshot_path.write_text(json.dumps({"error": workbench_error}, indent=2) + "\n", encoding="utf-8")
        html_path.write_text(f"<html><body><pre>{workbench_error}</pre></body></html>\n", encoding="utf-8")
        workbench_snapshot_path = str(snapshot_path)
        workbench_html_path = str(html_path)

    bucket_counts: dict[str, int] = {}
    for result in packet_results:
        bucket_counts[result.bucket] = bucket_counts.get(result.bucket, 0) + 1
    return FOMSisoShowcaseReport(
        title=title,
        packet_results=tuple(packet_results),
        workbench_snapshot_path=workbench_snapshot_path,
        workbench_html_path=workbench_html_path,
        workbench_error=workbench_error,
        bucket_counts=bucket_counts,
    )


def _render_markdown(report: FOMSisoShowcaseReport) -> str:
    lines = [
        f"# {report.title}",
        "",
        f"- packets: `{len(report.packet_results)}`",
        f"- passed: `{report.passed}`",
        f"- workbench snapshot: `{report.workbench_snapshot_path}`",
        f"- workbench html: `{report.workbench_html_path}`",
    ]
    if report.workbench_error is not None:
        lines.append(f"- workbench error: `{report.workbench_error}`")
    lines.extend(["", "## Packet Summary", "", "| Packet | Edition | Scope | Expected | Actual | Validate | Round Trip | Overview |", "| --- | ---: | --- | --- | --- | --- | --- | --- |"])
    for result in report.packet_results:
        lines.append(
            "| "
            + " | ".join(
                (
                    result.id,
                    str(result.year),
                    result.edition_scope,
                    ", ".join(result.expected_buckets),
                    result.bucket,
                    "pass" if result.validation_passed else result.validation_verdict,
                    "pass" if result.roundtrip_passed else (result.roundtrip_error or "failed"),
                    "pass" if result.overview_passed else (result.overview_error or "failed"),
                )
            )
            + " |"
        )
    for showcase in _SHOWCASE_GROUPS:
        matching = [row for row in report.packet_results if row.id in showcase.packet_ids]
        if not matching:
            continue
        lines.extend(["", f"## {showcase.title}", "", showcase.summary, ""])
        for step_index, step in enumerate(showcase.event_ladder, start=1):
            lines.append(f"{step_index}. {step}")
        for result in matching:
            lines.extend(
                [
                    "",
                    f"### {result.title}",
                    "",
                    f"- Summary: {result.summary}",
                    f"- Bucket: `{result.bucket}`",
                    f"- Expected bucket(s): `{', '.join(result.expected_buckets)}`",
                    f"- Matches expectation: `{result.matches_expectation}`",
                    f"- Members: `{len(result.member_ids)}`",
                    f"- Object classes: `{result.object_class_count}`",
                    f"- Interaction classes: `{result.interaction_class_count}`",
                    f"- Datatypes: `{result.datatype_count}`",
                    f"- Dimensions: `{', '.join(result.dimensions) if result.dimensions else 'none'}`",
                    f"- Validation packet: `{result.validation_md_path}`",
                    f"- Round-trip packet: `{result.roundtrip_md_path}`",
                    f"- Overview packet: `{result.overview_md_path or 'n/a'}`",
                ]
            )
            if result.feature_highlights:
                lines.append("- Highlights:")
                for highlight in result.feature_highlights:
                    lines.append(f"  - {highlight}")
            if result.validation_error is not None:
                lines.append(f"- Validation error: `{result.validation_error}`")
            if result.roundtrip_error is not None:
                lines.append(f"- Round-trip error: `{result.roundtrip_error}`")
            if result.overview_error is not None:
                lines.append(f"- Overview error: `{result.overview_error}`")
    lines.extend(
        [
            "",
            "## Operator Commands",
            "",
            "- `./tools/fom-siso-showcase`",
            "- `./tools/fom-siso-audit`",
            "- `./tools/fom-workbench --html`",
            "- `./tools/fom-stress`",
        ]
    )
    return "\n".join(lines) + "\n"


def write_fom_siso_showcase(
    output_root: str | Path,
    *,
    packet_ids: tuple[str, ...] | None = None,
    strict_identification: bool = False,
    title: str = "High-Value SISO FOM Showcase",
) -> tuple[Path, Path, FOMSisoShowcaseReport]:
    report = build_fom_siso_showcase(
        output_root=output_root,
        packet_ids=packet_ids,
        strict_identification=strict_identification,
        title=title,
    )
    output_path = Path(output_root)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "fom_siso_showcase_report.json"
    md_path = output_path / "fom_siso_showcase_report.md"
    json_path.write_text(report.to_json() + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown(report), encoding="utf-8")
    return json_path, md_path, report


__all__ = [
    "FOMSisoShowcasePacketResult",
    "FOMSisoShowcaseReport",
    "build_fom_siso_showcase",
    "write_fom_siso_showcase",
]
