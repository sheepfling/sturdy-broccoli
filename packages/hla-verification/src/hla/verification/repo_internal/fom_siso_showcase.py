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
    validation_edition: int | None = None


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
    validation_edition: int
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
    analysis_note: str | None

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
        include_path_fragments=("Link_16_v2.0.xml",),
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
        expected_buckets=("roundtrip-only-stress",),
        summary="This is the main clean tactical federation showcase: the current normative RPR pack, ordered and merged as intended.",
        family="siso-rpr-3.0",
        include_path_fragments=("Annex A Files Normative",),
        exclude_path_fragments=("Annex B Files Informative",),
        validation_edition=2010,
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
        records = tuple(by_id[member_id] for member_id in spec.member_ids if member_id in by_id)
        if not records and spec.include_path_fragments:
            records = tuple(
                record
                for record in inventory_records()
                if all(fragment in record.path for fragment in spec.include_path_fragments)
            )
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


def _analysis_note(*, spec: ShowcasePacketSpec, validation_verdict: str, roundtrip_error: str | None) -> str | None:
    if spec.validation_edition is not None and spec.validation_edition != spec.year:
        return (
            f"Validated on the {spec.validation_edition} compatibility lane because the XML is not native {spec.year} namespace/schema material; "
            f"the packet still stresses the {spec.year} round-trip path."
        )
    if validation_verdict == "nonconforming" and roundtrip_error is None:
        return "The packet parses and cycles, but the current validator still classifies it as nonconforming."
    if roundtrip_error is not None and "XML round-trip signature mismatch" in roundtrip_error:
        return "The packet merges and serializes, but serializer-normalization parity is not exact on the current round-trip path."
    return None


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
        validation_edition = spec.validation_edition or spec.year

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
                edition=str(validation_edition),
                strict_identification=strict_identification,
                title=f"{spec.title} | FOM Validation",
            )
            validation_html = write_fom_validation_html(
                source_paths,
                output_dir=validation_output_dir,
                edition=str(validation_edition),
                strict_identification=strict_identification,
                title=f"{spec.title} | FOM Validation",
            )
            validation_html_path = str(validation_html)
            packet_validation_row = validation_report.load_set_reports[0] if validation_report.load_set_reports else None
            validation_passed = packet_validation_row.passed if packet_validation_row is not None else False
            validation_verdict = packet_validation_row.verdict if packet_validation_row is not None else (
                validation_report.source_reports[0].verdict if validation_report.source_reports else "parse-failed"
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
                validation_edition=validation_edition,
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
                analysis_note=_analysis_note(
                    spec=spec,
                    validation_verdict=validation_verdict,
                    roundtrip_error=roundtrip_error,
                ),
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
        lines.extend(["", "## Packet Summary", "", "| Packet | Round-Trip Edition | Validation Edition | Scope | Expected | Actual | Validate | Round Trip | Overview |", "| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |"])
    for result in report.packet_results:
        lines.append(
            "| "
            + " | ".join(
                (
                    result.id,
                    str(result.year),
                    str(result.validation_edition),
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
                    f"- Validation edition: `{result.validation_edition}`",
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
            if result.analysis_note is not None:
                lines.append(f"- Analysis note: {result.analysis_note}")
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


def _html_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _render_html(report: FOMSisoShowcaseReport) -> str:
    payload = report.to_json()
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_html_escape(report.title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4efe4;
      --panel: #fffdf7;
      --ink: #1f2426;
      --muted: #5b645f;
      --line: #d7cfbe;
      --accent: #9f5c24;
      --good: #2f6b4f;
      --warn: #916b12;
      --bad: #8a2f2f;
    }}
    body {{
      margin: 0;
      font: 15px/1.5 ui-sans-serif, system-ui, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, #fff1cf 0, rgba(255,241,207,.65) 20%, transparent 50%),
        linear-gradient(180deg, #fbf7ed 0, var(--bg) 100%);
    }}
    main {{ max-width: 1320px; margin: 0 auto; padding: 24px; }}
    h1, h2, h3 {{ margin: 0 0 12px; }}
    p {{ margin: 0 0 12px; }}
    .hero, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: 0 14px 40px rgba(58, 45, 24, 0.08);
    }}
    .hero {{ padding: 20px; margin-bottom: 18px; }}
    .hero-grid {{
      display: grid;
      gap: 14px;
      grid-template-columns: 1.6fr 1fr;
      align-items: start;
    }}
    .metric-grid {{
      display: grid;
      gap: 10px;
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }}
    .metric {{
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #fff;
    }}
    .metric .label {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }}
    .metric .value {{ font-size: 24px; font-weight: 700; }}
    .layout {{
      display: grid;
      gap: 16px;
      grid-template-columns: 320px 1fr;
    }}
    .panel {{ padding: 16px; }}
    .cards {{ display: grid; gap: 10px; }}
    .card {{
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #fff;
      cursor: pointer;
    }}
    .card.active {{ outline: 2px solid var(--accent); }}
    .muted {{ color: var(--muted); }}
    .status-good {{ color: var(--good); font-weight: 700; }}
    .status-warn {{ color: var(--warn); font-weight: 700; }}
    .status-bad {{ color: var(--bad); font-weight: 700; }}
    .chip-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 0; }}
    .chip {{
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: #fff;
      font-size: 12px;
    }}
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }}
    input, select {{
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: #fff;
      color: var(--ink);
    }}
    input {{ flex: 1 1 220px; }}
    .detail-grid {{
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      margin: 14px 0;
    }}
    .subpanel {{
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #fff;
    }}
    ol, ul {{ margin: 0; padding-left: 18px; }}
    li {{ margin-bottom: 6px; }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    code {{
      background: #f6f0e5;
      padding: 2px 6px;
      border-radius: 6px;
    }}
    .artifact-list a {{ display: block; margin-bottom: 6px; }}
    @media (max-width: 980px) {{
      .hero-grid, .layout, .detail-grid {{ grid-template-columns: 1fr; }}
      .metric-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <div class="hero-grid">
      <div>
        <h1>{_html_escape(report.title)}</h1>
        <p class="muted">Standards-backed showcase packets for Link 16, RPR 3.0, and Space FOM across validation, JSON cycle, overview, and workbench surfaces.</p>
        <div class="chip-row">
          <span class="chip">workbench snapshot: {_html_escape(report.workbench_snapshot_path)}</span>
          <span class="chip">workbench html: {_html_escape(report.workbench_html_path)}</span>
        </div>
      </div>
      <div class="metric-grid">
        <div class="metric"><div class="label">Packets</div><div class="value">{len(report.packet_results)}</div></div>
        <div class="metric"><div class="label">Passed</div><div class="value">{sum(1 for row in report.packet_results if row.matches_expectation)}</div></div>
        <div class="metric"><div class="label">Stress</div><div class="value">{sum(1 for row in report.packet_results if row.bucket == "roundtrip-only-stress")}</div></div>
        <div class="metric"><div class="label">Fail Fast</div><div class="value">{sum(1 for row in report.packet_results if row.bucket == "parse-fail-fast")}</div></div>
      </div>
    </div>
  </section>
  <section class="panel" style="margin-bottom:16px;">
    <h2>Lane Legend</h2>
    <div class="detail-grid">
      <div class="subpanel">
        <h3>template-fail-fast</h3>
        <p class="muted">Template-like or incomplete modules that should be rejected with stable diagnostics.</p>
      </div>
      <div class="subpanel">
        <h3>modular-load-merge</h3>
        <p class="muted">Ordered multi-module families used to prove load and merge semantics before stronger runtime claims.</p>
      </div>
      <div class="subpanel">
        <h3>roundtrip-stress</h3>
        <p class="muted">Packets that are primarily useful for parser, serializer-normalization, and JSON-cycle pressure.</p>
      </div>
      <div class="subpanel">
        <h3>runtime-federate-scenarios</h3>
        <p class="muted">Runtime-backed scenario families with meaningful event sequencing and federate behavior.</p>
      </div>
      <div class="subpanel">
        <h3>showcase-packets</h3>
        <p class="muted">Curated demo packets that gather validator, round-trip, overview, and workbench artifacts into one display surface.</p>
      </div>
      <div class="subpanel">
        <h3>schema-lane</h3>
        <p class="muted">Pure XML/XSD conformance lanes that should stay separate from merge and runtime proof claims.</p>
      </div>
    </div>
  </section>
  <section class="layout">
    <aside class="panel">
      <div class="toolbar">
        <input id="filterBox" type="search" placeholder="Filter by family, packet, or bucket">
        <select id="showcaseBox">
          <option value="all">All showcases</option>
        </select>
      </div>
      <div id="cardHost" class="cards"></div>
    </aside>
    <section class="panel">
      <div id="detailHost"></div>
    </section>
  </section>
</main>
<script type="application/json" id="payload">{_html_escape(payload)}</script>
<script>
const payload = JSON.parse(document.getElementById("payload").textContent);
const cardHost = document.getElementById("cardHost");
const detailHost = document.getElementById("detailHost");
const filterBox = document.getElementById("filterBox");
const showcaseBox = document.getElementById("showcaseBox");
let activeId = payload.packet_results[0]?.id || null;

function badgeClass(bucket) {{
  if (bucket === "validate-clean") return "status-good";
  if (bucket === "roundtrip-only-stress") return "status-warn";
  return "status-bad";
}}

function enrichShowcaseOptions() {{
  showcaseBox.innerHTML += payload.showcases.map((group) => `<option value="${{group.id}}">${{group.title}}</option>`).join("");
}}

function filteredRows() {{
  const filter = filterBox.value.toLowerCase();
  const showcase = showcaseBox.value;
  return payload.packet_results.filter((row) => {{
    if (showcase !== "all" && row.showcase_id !== showcase) return false;
    return JSON.stringify(row).toLowerCase().includes(filter);
  }});
}}

function renderCards() {{
  const rows = filteredRows();
  if (!rows.length) {{
    cardHost.innerHTML = '<p class="muted">No packets match the current filter.</p>';
    detailHost.innerHTML = '<p class="muted">No detail available.</p>';
    return;
  }}
  if (!rows.some((row) => row.id === activeId)) activeId = rows[0].id;
  cardHost.innerHTML = rows.map((row) => `
    <div class="card ${{row.id === activeId ? "active" : ""}}" data-id="${{row.id}}">
      <div><strong>${{row.title}}</strong></div>
      <div class="muted">${{row.showcase_title}} | scope: ${{row.edition_scope}}</div>
      <div class="muted">round-trip edition ${{row.year}} | validation edition ${{row.validation_edition}}</div>
      <div class="${{badgeClass(row.bucket)}}">${{row.bucket}}</div>
    </div>
  `).join("");
  Array.from(cardHost.querySelectorAll(".card")).forEach((node) => node.addEventListener("click", () => {{
    activeId = node.dataset.id;
    renderCards();
    renderDetail();
  }}));
  renderDetail();
}}

function linkIf(path, label) {{
  if (!path) return '<span class="muted">n/a</span>';
  return `<a href="${{path}}">${{label}}</a>`;
}}

function renderDetail() {{
  const row = payload.packet_results.find((item) => item.id === activeId);
  if (!row) {{
    detailHost.innerHTML = '<p class="muted">No detail available.</p>';
    return;
  }}
  const group = payload.showcases.find((item) => item.id === row.showcase_id);
  detailHost.innerHTML = `
    <h2>${{row.title}}</h2>
    <p class="muted">${{row.summary}}</p>
    <div class="chip-row">
      <span class="chip">actual: ${{row.bucket}}</span>
      <span class="chip">expected: ${{row.expected_buckets.join(", ")}}</span>
      <span class="chip">round-trip edition: ${{row.year}}</span>
      <span class="chip">validation edition: ${{row.validation_edition}}</span>
      <span class="chip">scope: ${{row.edition_scope}}</span>
    </div>
    <div class="detail-grid">
      <div class="subpanel">
        <h3>Packet Status</h3>
        <p><strong>Validation:</strong> ${{row.validation_verdict}}</p>
        <p><strong>Round trip:</strong> ${{row.roundtrip_passed ? "pass" : (row.roundtrip_error || "failed")}}</p>
        <p><strong>Overview:</strong> ${{row.overview_passed ? "pass" : (row.overview_error || "failed")}}</p>
        <p><strong>Matches expectation:</strong> ${{row.matches_expectation}}</p>
        ${{row.analysis_note ? `<p><strong>Analysis note:</strong> ${{row.analysis_note}}</p>` : ""}}
      </div>
      <div class="subpanel">
        <h3>Structure</h3>
        <p><strong>Members:</strong> ${{row.member_ids.length}}</p>
        <p><strong>Object classes:</strong> ${{row.object_class_count}}</p>
        <p><strong>Interaction classes:</strong> ${{row.interaction_class_count}}</p>
        <p><strong>Datatypes:</strong> ${{row.datatype_count}}</p>
        <p><strong>Dimensions:</strong> ${{row.dimensions.length ? row.dimensions.join(", ") : "none"}}</p>
      </div>
      <div class="subpanel">
        <h3>Artifacts</h3>
        <div class="artifact-list">
          ${{linkIf(row.validation_html_path, "validation html")}}
          ${{linkIf(row.validation_md_path, "validation markdown")}}
          ${{linkIf(row.validation_json_path, "validation json")}}
          ${{linkIf(row.roundtrip_md_path, "roundtrip markdown")}}
          ${{linkIf(row.roundtrip_json_path, "roundtrip json")}}
          ${{linkIf(row.overview_html_path, "overview html")}}
          ${{linkIf(row.overview_md_path, "overview markdown")}}
          ${{linkIf(row.overview_json_path, "overview json")}}
          ${{linkIf(payload.workbench_html_path, "showcase workbench html")}}
        </div>
      </div>
      <div class="subpanel">
        <h3>Highlights</h3>
        <ul>${{row.feature_highlights.map((item) => `<li>${{item}}</li>`).join("") || "<li>none</li>"}}</ul>
      </div>
    </div>
    <div class="subpanel" style="margin-bottom:12px;">
      <h3>Event Ladder</h3>
      <ol>${{(group?.event_ladder || []).map((item) => `<li>${{item}}</li>`).join("")}}</ol>
    </div>
    <div class="subpanel">
      <h3>Source Paths</h3>
      <ul>${{row.source_paths.map((path) => `<li><code>${{path}}</code></li>`).join("")}}</ul>
    </div>
  `;
}}

filterBox.addEventListener("input", renderCards);
showcaseBox.addEventListener("change", renderCards);
enrichShowcaseOptions();
renderCards();
</script>
</body>
</html>
"""


def write_fom_siso_showcase(
    output_root: str | Path,
    *,
    packet_ids: tuple[str, ...] | None = None,
    strict_identification: bool = False,
    title: str = "High-Value SISO FOM Showcase",
) -> tuple[Path, Path, Path, FOMSisoShowcaseReport]:
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
    html_path = output_path / "fom_siso_showcase.html"
    json_path.write_text(report.to_json() + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown(report), encoding="utf-8")
    html_path.write_text(_render_html(report), encoding="utf-8")
    return json_path, md_path, html_path, report


__all__ = [
    "FOMSisoShowcasePacketResult",
    "FOMSisoShowcaseReport",
    "build_fom_siso_showcase",
    "write_fom_siso_showcase",
]
