from __future__ import annotations

# pyright: reportArgumentType=false, reportGeneralTypeIssues=false
import csv
import json
import os
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from .requirements import load_canonical_requirement_catalog, survey_requirement_artifacts

OPEN_STATUSES = frozenset({"partial", "planned", "seeded"})
TRANSPORT_TERMS = ("transport", "grpc", "rest", "equivalence")
CANONICAL_2010_REL = "requirements/2010/canonical_requirements.json"


@dataclass(frozen=True, slots=True)
class BacklogRow:
    family: str
    source_file: str
    requirement_id: str
    clause: str
    item_name: str
    kind: str
    status: str
    acceptance_tests: tuple[str, ...]
    implementation_areas: tuple[str, ...]
    notes: str
    requirement_text: str


@dataclass(frozen=True, slots=True)
class BacklogQueueItem:
    queue_item: str
    clause: str
    open_row_count: int
    statuses: dict[str, int]
    kinds: dict[str, int]
    requirement_ids: tuple[str, ...]
    acceptance_tests: tuple[str, ...]
    implementation_areas: tuple[str, ...]
    suggested_next_action: str


@dataclass(frozen=True, slots=True)
class BacklogFamily:
    family: str
    description: str
    open_row_count: int
    queue_item_count: int
    statuses: dict[str, int]
    kinds: dict[str, int]
    queue_items: tuple[BacklogQueueItem, ...]


def _read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [{key: value or "" for key, value in row.items()} for row in csv.DictReader(handle)]


def _split_values(raw: str) -> tuple[str, ...]:
    values = [part.strip() for part in raw.split(";")]
    return tuple(value for value in values if value)


def _normalize_clause(raw: str) -> str:
    text = raw.strip()
    return text.removeprefix("Clause ").strip() if text else "-"


def _queue_sort_key(item: BacklogQueueItem) -> tuple[int, int, str]:
    planned = item.statuses.get("planned", 0)
    seeded = item.statuses.get("seeded", 0)
    return (-planned, -seeded, item.queue_item)


def _derive_next_action(kinds: Counter[str], statuses: Counter[str], family: str, rows: tuple[BacklogRow, ...]) -> str:
    if family == "Transports":
        return "Add native/gRPC/REST parity coverage or carve out the supported subset explicitly."
    if (
        family == "Federation Management"
        and set(kinds) == {"EFF"}
        and all(row.source_file == "requirements/2010/hla1516_1_clause_4_fm_service_decomposition.csv" for row in rows)
    ):
        return (
            "Optional: tighten this bounded FM state-vector tail into a single direct witness if broader granularity is desired; "
            "otherwise preserve the explicit bounded owner reading."
        )
    if statuses.get("seeded"):
        return "Split the seeded row into implementation-driving subrequirements with direct tests."
    if kinds.get("MOM"):
        return "Add direct MOM observer or service-reporting evidence for the remaining open rows."
    if kinds.get("PRE") or kinds.get("EXC"):
        return "Tighten negative-path coverage until the supported precondition and exception envelope is explicit."
    if kinds.get("TEST"):
        return "Promote the remaining acceptance-test slice with direct executable coverage and transport parity where applicable."
    if kinds.get("EFF") or kinds.get("ARG") or kinds.get("SVC") or kinds.get("SEM"):
        return "Add focused runtime or state-transition evidence for the remaining behavioral slice."
    if kinds.get("CB") or kinds.get("CB_ORDER") or kinds.get("CB_PAYLOAD"):
        return "Add isolated callback sequence and payload assertions for the remaining callback slice."
    return "Promote the remaining partial rows with narrower direct evidence or explicit supported-subset notes."


def _collect_base_rows(
    project_root: Path,
    family: str,
    source_file: str,
    status_field: str,
    requirement_id_field: str,
    clause_field: str,
    item_name_field: str,
    kind_field: str,
    tests_field: str,
    implementation_field: str,
    notes_field: str,
    text_field: str,
) -> list[BacklogRow]:
    rows: list[BacklogRow] = []
    for raw in _read_csv_dicts(project_root / source_file):
        status = raw[status_field].strip().lower()
        if status not in OPEN_STATUSES:
            continue
        rows.append(
            BacklogRow(
                family=family,
                source_file=source_file,
                requirement_id=raw[requirement_id_field].strip(),
                clause=_normalize_clause(raw[clause_field]),
                item_name=raw[item_name_field].strip() or raw[requirement_id_field].strip(),
                kind=raw[kind_field].strip() or "-",
                status=status,
                acceptance_tests=_split_values(raw[tests_field]),
                implementation_areas=_split_values(raw[implementation_field]),
                notes=raw[notes_field].strip(),
                requirement_text=raw[text_field].strip(),
            )
        )
    return rows


def _build_queue_items(rows: list[BacklogRow], family: str) -> tuple[BacklogQueueItem, ...]:
    grouped: dict[tuple[str, str], list[BacklogRow]] = defaultdict(list)
    for row in rows:
        grouped[(row.clause, row.item_name)].append(row)

    items: list[BacklogQueueItem] = []
    for (clause, item_name), group in grouped.items():
        statuses = Counter(row.status for row in group)
        kinds = Counter(row.kind for row in group)
        requirement_ids = tuple(dict.fromkeys(row.requirement_id for row in group))
        acceptance_tests = tuple(
            dict.fromkeys(test for row in group for test in row.acceptance_tests)
        )
        implementation_areas = tuple(
            dict.fromkeys(area for row in group for area in row.implementation_areas)
        )
        items.append(
            BacklogQueueItem(
                queue_item=item_name,
                clause=clause,
                open_row_count=len(group),
                statuses=dict(sorted(statuses.items())),
                kinds=dict(sorted(kinds.items())),
                requirement_ids=requirement_ids,
                acceptance_tests=acceptance_tests,
                implementation_areas=implementation_areas,
                suggested_next_action=_derive_next_action(kinds, statuses, family, tuple(group)),
            )
        )
    return tuple(sorted(items, key=_queue_sort_key))


def _build_family(family: str, description: str, rows: list[BacklogRow]) -> BacklogFamily:
    statuses = Counter(row.status for row in rows)
    kinds = Counter(row.kind for row in rows)
    queue_items = _build_queue_items(rows, family)
    return BacklogFamily(
        family=family,
        description=description,
        open_row_count=len(rows),
        queue_item_count=len(queue_items),
        statuses=dict(sorted(statuses.items())),
        kinds=dict(sorted(kinds.items())),
        queue_items=queue_items,
    )


def _open_omt_rows(project_root: Path) -> list[BacklogRow]:
    rows: list[BacklogRow] = []
    source_file = "requirements/2010/hla1516_2_omt.csv"
    for raw in _read_csv_dicts(project_root / source_file):
        status = raw["status"].strip().lower()
        if status not in OPEN_STATUSES:
            continue
        topic = raw["topic"].strip()
        text = " ".join(
            [
                raw["clause"],
                topic,
                raw["requirement_text"],
                raw["derived_interpretation"],
                raw["notes"],
            ]
        ).lower()
        family = "XML" if ("xml" in text or "schema" in text or "annex e" in text) else "OMT"
        rows.append(
            BacklogRow(
                family=family,
                source_file=source_file,
                requirement_id=raw["requirement_id"].strip(),
                clause=_normalize_clause(raw["clause"]),
                item_name=topic or raw["requirement_id"].strip(),
                kind="SEED",
                status=status,
                acceptance_tests=_split_values(raw["test_id"]),
                implementation_areas=_split_values(raw["implementation_target"]),
                notes=raw["notes"].strip(),
                requirement_text=raw["requirement_text"].strip(),
            )
        )
    return rows


def _filter_rows(rows: list[BacklogRow], predicate: Callable[[BacklogRow], bool]) -> list[BacklogRow]:
    return [row for row in rows if predicate(row)]


def _candidate_project_roots() -> tuple[Path, ...]:
    raw_root = os.environ.get("HLA2010_PROJECT_ROOT")
    candidates: list[Path] = []
    if raw_root:
        candidates.append(Path(raw_root).expanduser().resolve())
    cwd = Path.cwd().resolve()
    candidates.extend((cwd, *cwd.parents))
    return tuple(dict.fromkeys(candidates))


def _resolve_project_root(project_root: Path | None = None) -> Path:
    if project_root is not None:
        return project_root.resolve()
    required_files = (
        "requirements/2010/hla1516_1_clause_4_fm_service_decomposition.csv",
        "requirements/2010/hla1516_1_clause_10_sup_detailed_reconciliation.csv",
        "requirements/2010/hla1516_2_omt.csv",
    )
    for candidate in _candidate_project_roots():
        if all((candidate / relative_path).is_file() for relative_path in required_files):
            return candidate
    raise ValueError(
        "project_root is required unless the current working tree contains the imported-HLA requirements artifacts"
    )


def build_imported_hla_backlog(project_root: Path | None = None) -> dict[str, object]:
    base = _resolve_project_root(project_root)
    canonical = load_canonical_requirement_catalog(base / CANONICAL_2010_REL)
    artifact_survey = survey_requirement_artifacts(base)
    artifact_families = {entry.path: entry.family for entry in artifact_survey.entries}
    families: list[BacklogFamily] = []

    base_specs = [
        (
            "Federation Management",
            "Clause 4 decomposition backlog for federation lifecycle and synchronization services.",
            "requirements/2010/hla1516_1_clause_4_fm_service_decomposition.csv",
            "status",
            "requirement_id",
            "clause",
            "service",
            "decomposition_kind",
            "test_id",
            "implementation_area",
            "notes",
            "requirement_text",
        ),
        (
            "Declaration Management",
            "Clause 5 packet-to-curated backlog for declaration services.",
            "requirements/2010/hla1516_1_clause_5_dm_detailed_reconciliation.csv",
            "current_status",
            "packet_requirement_id",
            "clause",
            "service_name",
            "reconciliation_kind",
            "current_test_id",
            "implementation_area",
            "notes",
            "requirement_text",
        ),
        (
            "Object Management",
            "Clause 6 packet-to-curated backlog for object-management services.",
            "requirements/2010/hla1516_1_clause_6_om_detailed_reconciliation.csv",
            "current_status",
            "packet_requirement_id",
            "clause",
            "service_name",
            "reconciliation_kind",
            "current_test_id",
            "implementation_area",
            "notes",
            "requirement_text",
        ),
        (
            "Ownership Management",
            "Clause 7 packet-to-curated backlog for ownership-management services.",
            "requirements/2010/hla1516_1_clause_7_own_detailed_reconciliation.csv",
            "current_status",
            "packet_requirement_id",
            "clause",
            "service_name",
            "reconciliation_kind",
            "current_test_id",
            "implementation_area",
            "notes",
            "requirement_text",
        ),
        (
            "Time Management",
            "Clause 8 packet-to-curated backlog for time-management services.",
            "requirements/2010/hla1516_1_clause_8_tm_detailed_reconciliation.csv",
            "current_status",
            "packet_requirement_id",
            "clause",
            "service_name",
            "reconciliation_kind",
            "current_test_id",
            "implementation_area",
            "notes",
            "requirement_text",
        ),
        (
            "Data Distribution Management",
            "Clause 9 packet-to-curated backlog for DDM services.",
            "requirements/2010/hla1516_1_clause_9_ddm_detailed_reconciliation.csv",
            "current_status",
            "packet_requirement_id",
            "clause",
            "service_name",
            "reconciliation_kind",
            "current_test_id",
            "implementation_area",
            "notes",
            "requirement_text",
        ),
        (
            "Support Services",
            "Clause 10 packet-to-curated backlog for support services.",
            "requirements/2010/hla1516_1_clause_10_sup_detailed_reconciliation.csv",
            "current_status",
            "packet_requirement_id",
            "clause",
            "service_name",
            "reconciliation_kind",
            "current_test_id",
            "implementation_area",
            "notes",
            "requirement_text",
        ),
    ]

    all_base_rows: list[BacklogRow] = []
    for spec in base_specs:
        family, description, *args = spec
        rows = _collect_base_rows(base, family, *args)
        all_base_rows.extend(rows)
        families.append(_build_family(family, description, rows))

    omt_rows = _open_omt_rows(base)
    omt_family_rows = _filter_rows(omt_rows, lambda row: row.family == "OMT")
    xml_family_rows = _filter_rows(omt_rows, lambda row: row.family == "XML")
    families.append(
        _build_family(
            "OMT",
            "Open IEEE 1516.2 OMT parser, merge, and model-structure backlog rows.",
            omt_family_rows,
        )
    )
    families.append(
        _build_family(
            "XML",
            "Open IEEE 1516.2 XML and schema-conformance backlog rows.",
            xml_family_rows,
        )
    )

    mom_rows = []
    for row in [*all_base_rows, *omt_rows]:
        text = " ".join([row.item_name, row.requirement_id, row.requirement_text]).lower()
        if row.kind == "MOM" or row.source_file.endswith("clause_11_mom_detailed_reconciliation.csv"):
            mom_rows.append(row)
            continue
        if " mim" in f" {text}" or "mom/" in text or "standard mim" in text or "mim " in f"{text} ":
            mom_rows.append(row)
    families.append(
        _build_family(
            "MOM/MIM",
            "Cross-cutting MOM observer, MOM service-reporting, and standard MIM backlog rows.",
            mom_rows,
        )
    )

    transport_rows = [
        row
        for row in [*all_base_rows, *omt_rows]
        if any(term in " ".join([row.item_name, row.requirement_id, row.requirement_text, row.notes]).lower() for term in TRANSPORT_TERMS)
    ]
    families.append(
        _build_family(
            "Transports",
            "Cross-cutting native/gRPC/REST transport-equivalence and transportation-type backlog rows.",
            transport_rows,
        )
    )

    order = {
        "Federation Management": 0,
        "Declaration Management": 1,
        "Object Management": 2,
        "Ownership Management": 3,
        "Time Management": 4,
        "Data Distribution Management": 5,
        "Support Services": 6,
        "MOM/MIM": 7,
        "OMT": 8,
        "XML": 9,
        "Transports": 10,
    }
    families = sorted(families, key=lambda family: order[family.family])
    total_open_rows = sum(family.open_row_count for family in families)
    total_queue_items = sum(family.queue_item_count for family in families)
    source_artifacts = sorted(
        {
            *[spec[2] for spec in base_specs],
            "requirements/2010/hla1516_2_omt.csv",
        }
    )
    return {
        "generated_from": (
            "canonical 2010 requirement catalog + mapping-bridge/import-history backlog projection"
        ),
        "canonical_requirement_artifact": CANONICAL_2010_REL,
        "canonical_requirement_row_count": canonical.row_count,
        "canonical_requirement_status_counts": dict(sorted(Counter(row.canonical_status for row in canonical.rows).items())),
        "backlog_surface_class": "generated-mapping-bridge-backlog",
        "source_artifacts": source_artifacts,
        "source_artifact_classes": {path: artifact_families.get(path, "") for path in source_artifacts},
        "total_open_rows": total_open_rows,
        "total_queue_items": total_queue_items,
        "families": [asdict(family) for family in families],
    }


def build_imported_hla_backlog_markdown(project_root: Path | None = None) -> list[str]:
    backlog = build_imported_hla_backlog(project_root)
    lines = [
        "# Imported HLA Requirements Backlog v1.0",
        "",
        "This generated backlog is a mapping-bridge work projection derived against the canonical 2010 requirement catalog.",
        "It does not define requirement truth. Canonical ownership stays in `requirements/2010/canonical_requirements.json`, while this packet only summarizes any remaining bridge-level implementation queue items.",
        "Some rows intentionally appear in multiple queues, especially `MOM/MIM` and `Transports`, because those are cross-cutting execution backlogs rather than mutually exclusive taxonomies.",
        "",
        f"- Canonical requirement artifact: {backlog['canonical_requirement_artifact']}",
        f"- Canonical requirement rows: {backlog['canonical_requirement_row_count']}",
        f"- Backlog surface class: {backlog['backlog_surface_class']}",
        f"- Total open rows: {backlog['total_open_rows']}",
        f"- Total queue items: {backlog['total_queue_items']}",
        f"- Families: {len(backlog['families'])}",
        "",
        "## Queue Summary",
        "",
        "| Family | Open rows | Queue items | Statuses | Dominant kinds |",
        "|---|---:|---:|---|---|",
    ]
    for family in backlog["families"]:
        kinds = family["kinds"]
        dominant_kinds = ", ".join(
            f"{kind}:{count}" for kind, count in sorted(kinds.items(), key=lambda item: (-item[1], item[0]))[:3]
        ) or "-"
        statuses = ", ".join(f"{status}:{count}" for status, count in family["statuses"].items()) or "-"
        lines.append(
            f"| {family['family']} | {family['open_row_count']} | {family['queue_item_count']} | {statuses} | {dominant_kinds} |"
        )
    lines.append("")

    for family in backlog["families"]:
        lines.extend(
            [
                f"## {family['family']}",
                "",
                family["description"],
                "",
                f"- Open rows: {family['open_row_count']}",
                f"- Queue items: {family['queue_item_count']}",
                f"- Statuses: {', '.join(f'{status}:{count}' for status, count in family['statuses'].items()) or '-'}",
                f"- Kinds: {', '.join(f'{kind}:{count}' for kind, count in family['kinds'].items()) or '-'}",
                "",
                "| Queue item | Clause | Open rows | Kinds | Requirement IDs | Acceptance tests | Next action |",
                "|---|---|---:|---|---|---|---|",
            ]
        )
        for item in family["queue_items"]:
            requirement_ids = ", ".join(item["requirement_ids"][:3])
            if len(item["requirement_ids"]) > 3:
                requirement_ids += f" (+{len(item['requirement_ids']) - 3} more)"
            acceptance_tests = ", ".join(item["acceptance_tests"][:3]) or "none yet"
            if len(item["acceptance_tests"]) > 3:
                acceptance_tests += f" (+{len(item['acceptance_tests']) - 3} more)"
            kinds = ", ".join(f"{kind}:{count}" for kind, count in item["kinds"].items())
            lines.append(
                f"| {item['queue_item']} | {item['clause']} | {item['open_row_count']} | {kinds} | {requirement_ids or '-'} | {acceptance_tests} | {item['suggested_next_action']} |"
            )
        lines.append("")
    return lines


def write_imported_hla_backlog(markdown_path: Path, json_path: Path, project_root: Path | None = None) -> dict[str, Path]:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    backlog = build_imported_hla_backlog(project_root)
    markdown_path.write_text("\n".join(build_imported_hla_backlog_markdown(project_root)) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(backlog, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"markdown": markdown_path, "json": json_path}
