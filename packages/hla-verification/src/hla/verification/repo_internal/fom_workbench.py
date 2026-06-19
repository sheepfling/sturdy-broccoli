"""Snapshot helpers for a future FOM workbench UI."""

from __future__ import annotations

import html
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from hla.rti1516e.fom import FOMCatalog, FOMResolutionError, FOMResolver, merge_fom_modules
from hla.verification.repo_internal.fom_inventory import FOMInventoryRecord, default_load_set_records, inventory_records
from hla.verification.repo_internal.fom_validate import write_fom_validation, write_fom_validation_html


@dataclass(frozen=True, slots=True)
class FOMWorkbenchNode:
    kind: str
    full_name: str
    parent_name: str | None
    declared_count: int
    total_count: int
    declared_names: tuple[str, ...]
    total_names: tuple[str, ...]
    datatype_hints: tuple[str, ...]
    lineage: tuple[str, ...]
    is_leaf: bool


@dataclass(frozen=True, slots=True)
class FOMWorkbenchFamily:
    scenario_family: str
    edition_classes: tuple[str, ...]
    baseline_kinds: tuple[str, ...]
    load_mode: str
    member_ids: tuple[str, ...]
    member_paths: tuple[str, ...]
    default_load_set_ids: tuple[str, ...]
    default_load_set_paths: tuple[str, ...]
    parse_status: str
    parse_error: str | None
    module_names: tuple[str, ...]
    object_class_count: int
    interaction_class_count: int
    datatype_count: int
    dimensions: tuple[str, ...]
    object_classes: tuple[str, ...]
    interaction_classes: tuple[str, ...]
    datatype_names: tuple[str, ...]
    object_nodes: tuple[FOMWorkbenchNode, ...]
    interaction_nodes: tuple[FOMWorkbenchNode, ...]
    validation_command: str | None
    validation_json_path: str | None
    validation_md_path: str | None
    validation_html_path: str | None


@dataclass(frozen=True, slots=True)
class FOMWorkbenchLoadSet:
    name: str
    member_ids: tuple[str, ...]
    member_paths: tuple[str, ...]
    parse_status: str
    parse_error: str | None
    module_names: tuple[str, ...]
    object_class_count: int
    interaction_class_count: int
    datatype_count: int
    dimensions: tuple[str, ...]
    object_classes: tuple[str, ...]
    interaction_classes: tuple[str, ...]
    datatype_names: tuple[str, ...]
    object_nodes: tuple[FOMWorkbenchNode, ...]
    interaction_nodes: tuple[FOMWorkbenchNode, ...]
    validation_command: str | None
    validation_json_path: str | None
    validation_md_path: str | None
    validation_html_path: str | None


@dataclass(frozen=True, slots=True)
class FOMWorkbenchSearchRow:
    source_name: str
    source_kind: str
    kind: str
    name: str
    parent_name: str | None
    lineage: tuple[str, ...]
    is_leaf: bool
    edition_classes: tuple[str, ...]
    baseline_kinds: tuple[str, ...]
    load_mode: str


@dataclass(frozen=True, slots=True)
class FOMWorkbenchDiff:
    left_family: str
    right_family: str
    comparable: bool
    reason: str | None
    shared_dimensions: tuple[str, ...]
    only_left_dimensions: tuple[str, ...]
    only_right_dimensions: tuple[str, ...]
    shared_object_classes: tuple[str, ...]
    only_left_object_classes: tuple[str, ...]
    only_right_object_classes: tuple[str, ...]
    shared_interaction_classes: tuple[str, ...]
    only_left_interaction_classes: tuple[str, ...]
    only_right_interaction_classes: tuple[str, ...]
    shared_datatype_names: tuple[str, ...]
    only_left_datatype_names: tuple[str, ...]
    only_right_datatype_names: tuple[str, ...]
    left_kind: str
    right_kind: str
    left_member_ids: tuple[str, ...]
    right_member_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FOMWorkbenchSnapshot:
    schema_version: int
    title: str
    capabilities: dict[str, object]
    entries: tuple[dict[str, object], ...]
    families: tuple[FOMWorkbenchFamily, ...]
    custom_load_sets: tuple[FOMWorkbenchLoadSet, ...]
    search_index: tuple[FOMWorkbenchSearchRow, ...]
    diffs: tuple[FOMWorkbenchDiff, ...]

    def to_json(self) -> str:
        return json.dumps(
            {
                "schema_version": self.schema_version,
                "title": self.title,
                "capabilities": self.capabilities,
                "entries": list(self.entries),
                "families": [asdict(row) for row in self.families],
                "custom_load_sets": [asdict(row) for row in self.custom_load_sets],
                "search_index": [asdict(row) for row in self.search_index],
                "diffs": [asdict(row) for row in self.diffs],
            },
            indent=2,
            sort_keys=True,
        )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


def _entry_payload(record: FOMInventoryRecord) -> dict[str, object]:
    absolute_path = _repo_root() / record.path
    return {
        "id": record.id,
        "path": record.path,
        "absolute_path": str(absolute_path),
        "edition_class": record.edition_class,
        "load_mode": record.load_mode,
        "baseline_kind": record.baseline_kind,
        "scenario_family": record.scenario_family,
        "notes": record.notes,
    }


def _spec_datatype_hints(spec: Any) -> tuple[str, ...]:
    datatype_map = getattr(spec, "attribute_datatypes", None) or getattr(spec, "parameter_datatypes", None) or {}
    hints: list[str] = []
    for value in datatype_map.values():
        if value and value not in hints:
            hints.append(value)
    return tuple(hints)


def _node_rows(specs: Iterable[Any], *, kind: str) -> tuple[FOMWorkbenchNode, ...]:
    specs = tuple(specs)
    spec_map = {spec.full_name: spec for spec in specs}
    child_counts: dict[str, int] = defaultdict(int)
    for spec in specs:
        if spec.parent_name:
            child_counts[spec.parent_name] += 1

    def lineage(name: str) -> tuple[str, ...]:
        chain: list[str] = []
        current = spec_map.get(name)
        while current is not None:
            chain.append(current.full_name)
            current = spec_map.get(current.parent_name or "")
        chain.reverse()
        return tuple(chain)

    rows: list[FOMWorkbenchNode] = []
    for spec in sorted(specs, key=lambda item: item.full_name):
        declared_names = tuple(getattr(spec, "declared_attributes", ()) or getattr(spec, "declared_parameters", ()))
        total_names = tuple(getattr(spec, "attributes", ()) or getattr(spec, "parameters", ()))
        rows.append(
            FOMWorkbenchNode(
                kind=kind,
                full_name=spec.full_name,
                parent_name=spec.parent_name,
                declared_count=len(declared_names),
                total_count=len(total_names),
                declared_names=declared_names,
                total_names=total_names,
                datatype_hints=_spec_datatype_hints(spec),
                lineage=lineage(spec.full_name),
                is_leaf=child_counts.get(spec.full_name, 0) == 0,
            )
        )
    return tuple(rows)


def _default_load_set(records: tuple[FOMInventoryRecord, ...]) -> tuple[FOMInventoryRecord, ...]:
    return default_load_set_records(records)


def _resolve_catalog(records: tuple[FOMInventoryRecord, ...]) -> tuple[tuple[str, ...], FOMCatalog]:
    resolver = FOMResolver()
    resolved = resolver.resolve_many(tuple((_repo_root() / record.path) for record in records))
    catalog = merge_fom_modules(resolved)
    module_names = tuple(module.name or str(module.source) for module in resolved)
    return module_names, catalog


def _family_summary(records: tuple[FOMInventoryRecord, ...], *, validation_output_dir: Path | None = None) -> FOMWorkbenchFamily:
    load_set = _default_load_set(records)
    parse_status = "ok"
    parse_error: str | None = None
    module_names: tuple[str, ...] = ()
    object_class_count = 0
    interaction_class_count = 0
    datatype_count = 0
    dimensions: tuple[str, ...] = ()
    object_classes: tuple[str, ...] = ()
    interaction_classes: tuple[str, ...] = ()
    datatype_names: tuple[str, ...] = ()
    object_nodes: tuple[FOMWorkbenchNode, ...] = ()
    interaction_nodes: tuple[FOMWorkbenchNode, ...] = ()
    validation_json_path: str | None = None
    validation_md_path: str | None = None
    validation_html_path: str | None = None
    validation_command = f"./tools/fom-validate --family {records[0].scenario_family} --html"
    try:
        module_names, catalog = _resolve_catalog(load_set)
        object_class_count = len(catalog.object_classes)
        interaction_class_count = len(catalog.interaction_classes)
        datatype_count = len(catalog.datatype_names)
        dimensions = tuple(catalog.dimensions)
        object_classes = tuple(sorted(catalog.object_classes))
        interaction_classes = tuple(sorted(catalog.interaction_classes))
        datatype_names = tuple(sorted(catalog.datatype_names))
        object_nodes = _node_rows(tuple(catalog.object_classes.values()), kind="object")
        interaction_nodes = _node_rows(tuple(catalog.interaction_classes.values()), kind="interaction")
        if validation_output_dir is not None:
            family_dir = validation_output_dir / records[0].scenario_family
            _, _, report = write_fom_validation(
                (),
                output_dir=family_dir,
                families=(records[0].scenario_family,),
            )
            html_path = write_fom_validation_html(
                (),
                output_dir=family_dir,
                families=(records[0].scenario_family,),
                title=report.title,
            )
            validation_json_path = str((family_dir / "fom_validation_report.json").relative_to(validation_output_dir.parent))
            validation_md_path = str((family_dir / "fom_validation_report.md").relative_to(validation_output_dir.parent))
            validation_html_path = str(html_path.relative_to(validation_output_dir.parent))
    except FOMResolutionError as exc:
        parse_status = "error"
        parse_error = str(exc)

    return FOMWorkbenchFamily(
        scenario_family=records[0].scenario_family,
        edition_classes=tuple(dict.fromkeys(record.edition_class for record in records)),
        baseline_kinds=tuple(dict.fromkeys(record.baseline_kind for record in records)),
        load_mode=records[0].load_mode,
        member_ids=tuple(record.id for record in records),
        member_paths=tuple(record.path for record in records),
        default_load_set_ids=tuple(record.id for record in load_set),
        default_load_set_paths=tuple(record.path for record in load_set),
        parse_status=parse_status,
        parse_error=parse_error,
        module_names=module_names,
        object_class_count=object_class_count,
        interaction_class_count=interaction_class_count,
        datatype_count=datatype_count,
        dimensions=dimensions,
        object_classes=object_classes,
        interaction_classes=interaction_classes,
        datatype_names=datatype_names,
        object_nodes=object_nodes,
        interaction_nodes=interaction_nodes,
        validation_command=validation_command,
        validation_json_path=validation_json_path,
        validation_md_path=validation_md_path,
        validation_html_path=validation_html_path,
    )


def _load_set_summary(name: str, records: tuple[FOMInventoryRecord, ...], *, validation_output_dir: Path | None = None) -> FOMWorkbenchLoadSet:
    parse_status = "ok"
    parse_error: str | None = None
    module_names: tuple[str, ...] = ()
    object_class_count = 0
    interaction_class_count = 0
    datatype_count = 0
    dimensions: tuple[str, ...] = ()
    object_classes: tuple[str, ...] = ()
    interaction_classes: tuple[str, ...] = ()
    datatype_names: tuple[str, ...] = ()
    object_nodes: tuple[FOMWorkbenchNode, ...] = ()
    interaction_nodes: tuple[FOMWorkbenchNode, ...] = ()
    validation_command = f"./tools/fom-validate {' '.join(record.path for record in records)} --html"
    validation_json_path: str | None = None
    validation_md_path: str | None = None
    validation_html_path: str | None = None
    try:
        module_names, catalog = _resolve_catalog(records)
        object_class_count = len(catalog.object_classes)
        interaction_class_count = len(catalog.interaction_classes)
        datatype_count = len(catalog.datatype_names)
        dimensions = tuple(catalog.dimensions)
        object_classes = tuple(sorted(catalog.object_classes))
        interaction_classes = tuple(sorted(catalog.interaction_classes))
        datatype_names = tuple(sorted(catalog.datatype_names))
        object_nodes = _node_rows(tuple(catalog.object_classes.values()), kind="object")
        interaction_nodes = _node_rows(tuple(catalog.interaction_classes.values()), kind="interaction")
        if validation_output_dir is not None:
            load_set_dir = validation_output_dir / name
            source_paths = tuple((_repo_root() / record.path) for record in records)
            _, _, report = write_fom_validation(
                source_paths,
                output_dir=load_set_dir,
                title=f"FOM Validation Report: {name}",
            )
            html_path = write_fom_validation_html(
                source_paths,
                output_dir=load_set_dir,
                title=report.title,
            )
            validation_json_path = str((load_set_dir / "fom_validation_report.json").relative_to(validation_output_dir.parent))
            validation_md_path = str((load_set_dir / "fom_validation_report.md").relative_to(validation_output_dir.parent))
            validation_html_path = str(html_path.relative_to(validation_output_dir.parent))
    except FOMResolutionError as exc:
        parse_status = "error"
        parse_error = str(exc)
    return FOMWorkbenchLoadSet(
        name=name,
        member_ids=tuple(record.id for record in records),
        member_paths=tuple(record.path for record in records),
        parse_status=parse_status,
        parse_error=parse_error,
        module_names=module_names,
        object_class_count=object_class_count,
        interaction_class_count=interaction_class_count,
        datatype_count=datatype_count,
        dimensions=dimensions,
        object_classes=object_classes,
        interaction_classes=interaction_classes,
        datatype_names=datatype_names,
        object_nodes=object_nodes,
        interaction_nodes=interaction_nodes,
        validation_command=validation_command,
        validation_json_path=validation_json_path,
        validation_md_path=validation_md_path,
        validation_html_path=validation_html_path,
    )


def _search_rows(
    families: tuple[FOMWorkbenchFamily, ...],
    custom_load_sets: tuple[FOMWorkbenchLoadSet, ...],
) -> tuple[FOMWorkbenchSearchRow, ...]:
    rows: list[FOMWorkbenchSearchRow] = []
    for family in families:
        for node in family.object_nodes:
            rows.append(
                FOMWorkbenchSearchRow(
                    source_name=family.scenario_family,
                    source_kind="family",
                    kind="object",
                    name=node.full_name,
                    parent_name=node.parent_name,
                    lineage=node.lineage,
                    is_leaf=node.is_leaf,
                    edition_classes=family.edition_classes,
                    baseline_kinds=family.baseline_kinds,
                    load_mode=family.load_mode,
                )
            )
        for node in family.interaction_nodes:
            rows.append(
                FOMWorkbenchSearchRow(
                    source_name=family.scenario_family,
                    source_kind="family",
                    kind="interaction",
                    name=node.full_name,
                    parent_name=node.parent_name,
                    lineage=node.lineage,
                    is_leaf=node.is_leaf,
                    edition_classes=family.edition_classes,
                    baseline_kinds=family.baseline_kinds,
                    load_mode=family.load_mode,
                )
            )
        for name in family.datatype_names:
            rows.append(
                FOMWorkbenchSearchRow(
                    source_name=family.scenario_family,
                    source_kind="family",
                    kind="datatype",
                    name=name,
                    parent_name=None,
                    lineage=(name,),
                    is_leaf=True,
                    edition_classes=family.edition_classes,
                    baseline_kinds=family.baseline_kinds,
                    load_mode=family.load_mode,
                )
            )
    for load_set in custom_load_sets:
        for node in load_set.object_nodes:
            rows.append(
                FOMWorkbenchSearchRow(
                    source_name=load_set.name,
                    source_kind="custom-load-set",
                    kind="object",
                    name=node.full_name,
                    parent_name=node.parent_name,
                    lineage=node.lineage,
                    is_leaf=node.is_leaf,
                    edition_classes=(),
                    baseline_kinds=(),
                    load_mode="custom",
                )
            )
        for node in load_set.interaction_nodes:
            rows.append(
                FOMWorkbenchSearchRow(
                    source_name=load_set.name,
                    source_kind="custom-load-set",
                    kind="interaction",
                    name=node.full_name,
                    parent_name=node.parent_name,
                    lineage=node.lineage,
                    is_leaf=node.is_leaf,
                    edition_classes=(),
                    baseline_kinds=(),
                    load_mode="custom",
                )
            )
        for name in load_set.datatype_names:
            rows.append(
                FOMWorkbenchSearchRow(
                    source_name=load_set.name,
                    source_kind="custom-load-set",
                    kind="datatype",
                    name=name,
                    parent_name=None,
                    lineage=(name,),
                    is_leaf=True,
                    edition_classes=(),
                    baseline_kinds=(),
                    load_mode="custom",
                )
            )
    return tuple(sorted(rows, key=lambda row: (row.source_name, row.kind, row.name)))


def _summary_diff(
    left_name: str,
    right_name: str,
    left_kind: str,
    right_kind: str,
    left_member_ids: tuple[str, ...],
    right_member_ids: tuple[str, ...],
    left_parse_status: str,
    right_parse_status: str,
    left_dimensions: tuple[str, ...],
    right_dimensions: tuple[str, ...],
    left_object_classes: tuple[str, ...],
    right_object_classes: tuple[str, ...],
    left_interaction_classes: tuple[str, ...],
    right_interaction_classes: tuple[str, ...],
    left_datatype_names: tuple[str, ...],
    right_datatype_names: tuple[str, ...],
) -> FOMWorkbenchDiff:
    comparable = left_parse_status == "ok" and right_parse_status == "ok"
    if not comparable:
        return FOMWorkbenchDiff(
            left_family=left_name,
            right_family=right_name,
            comparable=False,
            reason=f"left={left_parse_status}, right={right_parse_status}",
            shared_dimensions=(),
            only_left_dimensions=(),
            only_right_dimensions=(),
            shared_object_classes=(),
            only_left_object_classes=(),
            only_right_object_classes=(),
            shared_interaction_classes=(),
            only_left_interaction_classes=(),
            only_right_interaction_classes=(),
            shared_datatype_names=(),
            only_left_datatype_names=(),
            only_right_datatype_names=(),
            left_kind=left_kind,
            right_kind=right_kind,
            left_member_ids=left_member_ids,
            right_member_ids=right_member_ids,
        )
    left_dims = set(left_dimensions)
    right_dims = set(right_dimensions)
    left_objects = set(left_object_classes)
    right_objects = set(right_object_classes)
    left_interactions = set(left_interaction_classes)
    right_interactions = set(right_interaction_classes)
    left_types = set(left_datatype_names)
    right_types = set(right_datatype_names)
    return FOMWorkbenchDiff(
        left_family=left_name,
        right_family=right_name,
        comparable=True,
        reason=None,
        shared_dimensions=tuple(sorted(left_dims & right_dims)),
        only_left_dimensions=tuple(sorted(left_dims - right_dims)),
        only_right_dimensions=tuple(sorted(right_dims - left_dims)),
        shared_object_classes=tuple(sorted(left_objects & right_objects)),
        only_left_object_classes=tuple(sorted(left_objects - right_objects)),
        only_right_object_classes=tuple(sorted(right_objects - left_objects)),
        shared_interaction_classes=tuple(sorted(left_interactions & right_interactions)),
        only_left_interaction_classes=tuple(sorted(left_interactions - right_interactions)),
        only_right_interaction_classes=tuple(sorted(right_interactions - left_interactions)),
        shared_datatype_names=tuple(sorted(left_types & right_types)),
        only_left_datatype_names=tuple(sorted(left_types - right_types)),
        only_right_datatype_names=tuple(sorted(right_types - left_types)),
        left_kind=left_kind,
        right_kind=right_kind,
        left_member_ids=left_member_ids,
        right_member_ids=right_member_ids,
    )


def _family_diff(left: FOMWorkbenchFamily, right: FOMWorkbenchFamily) -> FOMWorkbenchDiff:
    return _summary_diff(
        left.scenario_family,
        right.scenario_family,
        "family",
        "family",
        left.default_load_set_ids,
        right.default_load_set_ids,
        left.parse_status,
        right.parse_status,
        left.dimensions,
        right.dimensions,
        left.object_classes,
        right.object_classes,
        left.interaction_classes,
        right.interaction_classes,
        left.datatype_names,
        right.datatype_names,
    )


def _diff_rows(
    families: tuple[FOMWorkbenchFamily, ...],
    custom_load_sets: tuple[FOMWorkbenchLoadSet, ...],
    diff_specs: tuple[tuple[str, str], ...],
) -> tuple[FOMWorkbenchDiff, ...]:
    rows: list[FOMWorkbenchDiff] = []
    for index, left in enumerate(families):
        for right in families[index + 1 :]:
            rows.append(_family_diff(left, right))
    if diff_specs:
        family_lookup = {family.scenario_family: family for family in families}
        custom_lookup = {load_set.name: load_set for load_set in custom_load_sets}
        for left_name, right_name in diff_specs:
            left = family_lookup.get(left_name) or custom_lookup.get(left_name)
            right = family_lookup.get(right_name) or custom_lookup.get(right_name)
            if left is None or right is None:
                continue
            if isinstance(left, FOMWorkbenchFamily):
                left_fields = (
                    left.default_load_set_ids,
                    left.parse_status,
                    left.dimensions,
                    left.object_classes,
                    left.interaction_classes,
                    left.datatype_names,
                    "family",
                )
            else:
                left_fields = (
                    left.member_ids,
                    left.parse_status,
                    left.dimensions,
                    left.object_classes,
                    left.interaction_classes,
                    left.datatype_names,
                    "custom-load-set",
                )
            if isinstance(right, FOMWorkbenchFamily):
                right_fields = (
                    right.default_load_set_ids,
                    right.parse_status,
                    right.dimensions,
                    right.object_classes,
                    right.interaction_classes,
                    right.datatype_names,
                    "family",
                )
            else:
                right_fields = (
                    right.member_ids,
                    right.parse_status,
                    right.dimensions,
                    right.object_classes,
                    right.interaction_classes,
                    right.datatype_names,
                    "custom-load-set",
                )
            rows.append(
                _summary_diff(
                    left_name,
                    right_name,
                    left_fields[6],
                    right_fields[6],
                    left_fields[0],
                    right_fields[0],
                    left_fields[1],
                    right_fields[1],
                    left_fields[2],
                    right_fields[2],
                    left_fields[3],
                    right_fields[3],
                    left_fields[4],
                    right_fields[4],
                    left_fields[5],
                    right_fields[5],
                )
            )
    return tuple(rows)


def _parse_custom_load_set_specs(
    custom_load_sets: Mapping[str, tuple[str, ...]] | None,
    *,
    validation_output_dir: Path | None = None,
) -> tuple[FOMWorkbenchLoadSet, ...]:
    if not custom_load_sets:
        return ()
    records_by_id = {record.id: record for record in inventory_records()}
    load_sets: list[FOMWorkbenchLoadSet] = []
    for name, member_ids in custom_load_sets.items():
        records = tuple(records_by_id[member_id] for member_id in member_ids if member_id in records_by_id)
        if not records:
            continue
        load_sets.append(_load_set_summary(name, records, validation_output_dir=validation_output_dir))
    return tuple(sorted(load_sets, key=lambda row: row.name))


def build_fom_workbench_snapshot(
    *,
    custom_load_sets: Mapping[str, tuple[str, ...]] | None = None,
    diff_specs: tuple[tuple[str, str], ...] = (),
    validation_output_dir: str | Path | None = None,
) -> FOMWorkbenchSnapshot:
    records = inventory_records()
    grouped: dict[str, list[FOMInventoryRecord]] = defaultdict(list)
    for record in records:
        grouped[record.scenario_family].append(record)

    validation_root = Path(validation_output_dir) if validation_output_dir is not None else None
    families = tuple(
        sorted(
            (_family_summary(tuple(group), validation_output_dir=validation_root) for _, group in grouped.items()),
            key=lambda row: row.scenario_family,
        )
    )
    custom_load_set_rows = _parse_custom_load_set_specs(custom_load_sets, validation_output_dir=validation_root)
    search_index = _search_rows(families, custom_load_set_rows)
    diffs = _diff_rows(families, custom_load_set_rows, diff_specs)
    return FOMWorkbenchSnapshot(
        schema_version=1,
        title="FOM Workbench Snapshot",
        capabilities={
            "display": True,
            "edit": True,
            "join_sets": True,
            "overlay": True,
            "inspect": True,
            "search": True,
        },
        entries=tuple(_entry_payload(record) for record in records),
        families=families,
        custom_load_sets=custom_load_set_rows,
        search_index=search_index,
        diffs=diffs,
    )


def write_fom_workbench_snapshot(
    *,
    output_dir: str | Path,
    custom_load_sets: Mapping[str, tuple[str, ...]] | None = None,
    diff_specs: tuple[tuple[str, str], ...] = (),
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    validation_output_dir = output_path / "validation_packets"
    snapshot = build_fom_workbench_snapshot(
        custom_load_sets=custom_load_sets,
        diff_specs=diff_specs,
        validation_output_dir=validation_output_dir,
    )
    json_path = output_path / "fom_workbench_snapshot.json"
    json_path.write_text(snapshot.to_json() + "\n", encoding="utf-8")
    return json_path


def apply_repo_owned_fom_edits(
    entry_id: str,
    *,
    description: str | None = None,
    add_keywords: tuple[str, ...] = (),
    add_notes: tuple[str, ...] = (),
    output_path: str | Path | None = None,
    in_place: bool = False,
) -> Path:
    records = {record.id: record for record in inventory_records()}
    record = records.get(entry_id)
    if record is None:
        raise KeyError(f"Unknown FOM inventory entry {entry_id!r}")
    if record.baseline_kind != "repo-owned":
        raise ValueError(f"Entry {entry_id!r} is not repo-owned and is not editable through the workbench")
    source_path = (_repo_root() / record.path).resolve()
    tree = ET.parse(source_path)
    root = tree.getroot()
    namespace = root.tag.partition("}")[0].lstrip("{")

    def qname(local: str) -> str:
        return f"{{{namespace}}}{local}" if namespace else local

    model_identification = next((child for child in list(root) if child.tag == qname("modelIdentification")), None)
    if model_identification is None:
        raise ValueError(f"FOM {entry_id!r} has no modelIdentification section")

    if description is not None:
        description_node = next((child for child in list(model_identification) if child.tag == qname("description")), None)
        if description_node is None:
            description_node = ET.SubElement(model_identification, qname("description"))
        description_node.text = description

    for keyword in add_keywords:
        if keyword.strip():
            keyword_node = ET.SubElement(model_identification, qname("keyword"))
            keyword_node.text = keyword.strip()

    if add_notes:
        notes_section = next((child for child in list(root) if child.tag == qname("notes")), None)
        if notes_section is None:
            notes_section = ET.SubElement(root, qname("notes"))
        for note_text in add_notes:
            note_text = note_text.strip()
            if not note_text:
                continue
            note = ET.SubElement(notes_section, qname("note"))
            label, separator, semantics = note_text.partition(": ")
            if separator:
                ET.SubElement(note, qname("label")).text = label
                ET.SubElement(note, qname("semantics")).text = semantics
            else:
                ET.SubElement(note, qname("semantics")).text = note_text

    if in_place:
        target_path = source_path
    else:
        if output_path is None:
            output_root = _repo_root() / "analysis" / "fom_workbench" / "edited"
            output_root.mkdir(parents=True, exist_ok=True)
            target_path = output_root / source_path.name
        else:
            target_path = Path(output_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)

    tree.write(target_path, encoding="utf-8", xml_declaration=True)
    return target_path


def _render_workbench_html(snapshot: FOMWorkbenchSnapshot) -> str:
    payload = snapshot.to_json()
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(snapshot.title)}</title>
  <style>
    :root {{
      --bg: #f2efe6;
      --panel: rgba(255,255,255,0.78);
      --ink: #10212b;
      --muted: #5c6a73;
      --line: rgba(16,33,43,0.12);
      --accent: #006d77;
      --accent-soft: rgba(0,109,119,0.10);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "IBM Plex Sans", "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 20% 0%, rgba(255,196,61,0.18), transparent 32%),
        radial-gradient(circle at 100% 20%, rgba(0,109,119,0.16), transparent 28%),
        linear-gradient(180deg, #faf7f0 0%, var(--bg) 100%);
    }}
    .wrap {{ max-width: 1400px; margin: 0 auto; padding: 28px; }}
    .hero {{
      display: grid;
      grid-template-columns: 1.7fr 1fr;
      gap: 20px;
      margin-bottom: 20px;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 20px;
      backdrop-filter: blur(12px);
      box-shadow: 0 14px 40px rgba(16,33,43,0.08);
    }}
    h1,h2,h3 {{ margin-top: 0; }}
    .muted {{ color: var(--muted); }}
    .pill {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      border: 1px solid rgba(0,109,119,0.16);
      margin: 0 8px 8px 0;
      font-size: 0.9rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 320px minmax(0, 1.15fr) minmax(0, 1fr);
      gap: 20px;
    }}
    input, select {{
      width: 100%;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.82);
      color: var(--ink);
      margin-bottom: 12px;
    }}
    button {{
      padding: 10px 14px;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.82);
      color: var(--ink);
      cursor: pointer;
    }}
    .family-list {{
      max-height: 72vh;
      overflow: auto;
      display: grid;
      gap: 10px;
    }}
    .family-card {{
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
      cursor: pointer;
      background: rgba(255,255,255,0.62);
    }}
    .family-card.active {{
      border-color: var(--accent);
      box-shadow: inset 0 0 0 1px var(--accent);
      background: rgba(0,109,119,0.06);
    }}
    .kv {{ display: grid; grid-template-columns: 180px 1fr; gap: 10px 14px; }}
    .kv dt {{ color: var(--muted); }}
    .list {{
      max-height: 220px;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 10px 14px;
      background: rgba(255,255,255,0.6);
    }}
    .list code {{ display: block; padding: 3px 0; }}
    .tree-list {{
      max-height: 260px;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 10px 14px;
      background: rgba(255,255,255,0.6);
    }}
    .tree-row {{
      cursor: pointer;
      padding: 4px 0;
      border-radius: 6px;
    }}
    .tree-row.active {{
      background: rgba(0,109,119,0.08);
    }}
    .toolbar {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 10px;
    }}
    .edit-box textarea {{
      width: 100%;
      min-height: 80px;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.82);
      color: var(--ink);
      font-family: inherit;
      margin-bottom: 10px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
    }}
    th, td {{
      text-align: left;
      border-bottom: 1px solid var(--line);
      padding: 8px 10px;
      vertical-align: top;
    }}
    .split {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }}
    .builder-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-top: 10px;
    }}
    .checkbox-list label {{
      display: block;
      margin-bottom: 8px;
      cursor: pointer;
    }}
    @media (max-width: 1100px) {{
      .hero, .grid, .split, .builder-grid {{ grid-template-columns: 1fr; }}
      .family-list {{ max-height: none; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <section class="panel">
        <h1>{html.escape(snapshot.title)}</h1>
        <p class="muted">Display, inspect, search, compare, and compose FOM load sets without reparsing XML in the browser. Repo-owned edit flow stays guarded and precomputed validation packets remain explicit.</p>
        <div>
          <span class="pill">families: {len(snapshot.families)}</span>
          <span class="pill">entries: {len(snapshot.entries)}</span>
          <span class="pill">search rows: {len(snapshot.search_index)}</span>
          <span class="pill">diff rows: {len(snapshot.diffs)}</span>
        </div>
      </section>
      <section class="panel">
        <h2>Capabilities</h2>
        <div id="capabilities"></div>
      </section>
    </div>
    <div class="grid">
      <section class="panel">
        <h2>Catalog</h2>
        <select id="catalog-mode">
          <option value="family">families</option>
          <option value="custom-load-set">custom load sets</option>
        </select>
        <input id="family-filter" type="search" placeholder="Filter families, custom load sets, editions, or load modes">
        <div id="family-list" class="family-list"></div>
        <div class="edit-box" style="margin-top: 14px;">
          <h3>Custom Load Set Builder</h3>
          <input id="builder-name" type="text" placeholder="saved load set name">
          <input id="builder-filter" type="search" placeholder="Filter baseline entries by id, family, edition, or path">
          <div id="builder-entry-list" class="list checkbox-list"></div>
          <div class="builder-grid">
            <button id="builder-save" type="button">save in browser</button>
            <button id="builder-clear" type="button">clear selection</button>
          </div>
          <div class="builder-grid">
            <button id="builder-export" type="button">export saved sets</button>
            <button id="builder-import" type="button">import saved sets</button>
          </div>
          <textarea id="builder-transfer" placeholder="paste exported custom load set JSON here"></textarea>
          <div id="builder-saved" class="list" style="margin-top: 10px;"></div>
          <div id="builder-command" class="list" style="margin-top: 10px;"></div>
        </div>
      </section>
      <section class="panel">
        <h2>Inspect</h2>
        <div id="inspect-panel" class="muted">Select a family or custom load set.</div>
        <div class="toolbar">
          <select id="tree-kind">
            <option value="object">object classes</option>
            <option value="interaction">interaction classes</option>
          </select>
          <input id="tree-filter" type="search" placeholder="Filter hierarchy">
        </div>
        <div id="tree-panel" class="tree-list"></div>
        <div id="node-panel" class="panel" style="padding: 14px; margin-top: 12px;"></div>
        <h3>Search Merged Names</h3>
        <input id="search-filter" type="search" placeholder="Search object, interaction, or datatype names">
        <table>
          <thead><tr><th>Kind</th><th>Name</th><th>Family</th></tr></thead>
          <tbody id="search-results"></tbody>
        </table>
        <div class="edit-box" style="margin-top: 14px;">
          <h3>Guarded Edit Flow</h3>
          <div id="edit-summary" class="muted"></div>
          <textarea id="edit-description" placeholder="Proposed description"></textarea>
          <input id="edit-keywords" type="text" placeholder="Keywords to append, comma-separated">
          <input id="edit-notes" type="text" placeholder="Notes to append, comma-separated">
          <div id="edit-command" class="list"></div>
        </div>
      </section>
      <section class="panel">
        <h2>Overlay / Diff</h2>
        <div class="split">
          <select id="left-family"></select>
          <select id="right-family"></select>
        </div>
        <div class="toolbar" style="margin-top: 10px;">
          <input id="custom-left" type="text" placeholder="custom left set: id1,id2">
          <input id="custom-right" type="text" placeholder="custom right set: id1,id2">
        </div>
        <div id="diff-panel" class="muted" style="margin-top: 14px;">Select two families to compare.</div>
      </section>
    </div>
  </div>
  <script>
    const snapshot = {payload};
    const browserStorageKey = "hla2010-fom-workbench-custom-load-sets";
    const familyMap = new Map(snapshot.families.map((family) => [family.scenario_family, family]));
    const diffMap = new Map(snapshot.diffs.map((diff) => [`${{diff.left_family}}::${{diff.right_family}}`, diff]));
    const entryMap = new Map(snapshot.entries.map((entry) => [entry.id, entry]));
    const fixedCustomLoadSetNames = new Set(snapshot.custom_load_sets.map((loadSet) => loadSet.name));
    const fixedFamilyNames = new Set(snapshot.families.map((family) => family.scenario_family));
    let browserCustomLoadSets = loadBrowserCustomLoadSets();
    let builderSelectedMemberIds = new Set();
    let selectedCatalogKind = snapshot.families[0] ? "family" : "custom-load-set";
    let selectedCatalogName = snapshot.families[0]?.scenario_family || customLoadSets()[0]?.name || null;
    let selectedNodeName = null;

    function setCapabilities() {{
      const host = document.getElementById("capabilities");
      host.innerHTML = Object.entries(snapshot.capabilities)
        .map(([key, value]) => `<span class="pill">${{key}}: ${{String(value)}}</span>`)
        .join("");
    }}

    function loadBrowserCustomLoadSets() {{
      try {{
        const raw = window.localStorage.getItem(browserStorageKey);
        if (!raw) return [];
        const parsed = JSON.parse(raw);
        if (!Array.isArray(parsed)) return [];
        return parsed.filter((row) => row && typeof row.name === "string" && Array.isArray(row.member_ids));
      }} catch (_error) {{
        return [];
      }}
    }}

    function saveBrowserCustomLoadSets() {{
      window.localStorage.setItem(browserStorageKey, JSON.stringify(browserCustomLoadSets));
    }}

    function normalizeBrowserCustomLoadSets(rows) {{
      if (!Array.isArray(rows)) return [];
      const normalized = [];
      for (const row of rows) {{
        if (!row || typeof row.name !== "string" || !Array.isArray(row.member_ids)) continue;
        const name = row.name.trim();
        if (!name || fixedFamilyNames.has(name) || fixedCustomLoadSetNames.has(name)) continue;
        const memberIds = [...new Set(row.member_ids.filter((id) => entryMap.has(id)))].sort();
        if (!memberIds.length) continue;
        normalized.push({{ name, member_ids: memberIds }});
      }}
      const deduped = new Map();
      for (const row of normalized) deduped.set(row.name, row);
      return [...deduped.values()].sort((left, right) => left.name.localeCompare(right.name));
    }}

    function customLoadSetCommand(name, memberIds) {{
      return `./tools/fom-workbench --html --custom-load-set ${{name}}=${{memberIds.join(",")}}`;
    }}

    function hydratedBrowserLoadSet(row) {{
      const members = row.member_ids.map((id) => entryMap.get(id)).filter(Boolean);
      const editionClasses = [...new Set(members.map((entry) => entry.edition_class))].sort();
      const baselineKinds = [...new Set(members.map((entry) => entry.baseline_kind))].sort();
      return {{
        name: row.name,
        member_ids: [...row.member_ids],
        member_paths: members.map((entry) => entry.path),
        parse_status: "browser-pending",
        parse_error: "Regenerate the workbench snapshot with the command below to compute parsed trees, diffs, and validation packets.",
        module_names: members.map((entry) => entry.path.split("/").slice(-1)[0]),
        object_class_count: 0,
        interaction_class_count: 0,
        datatype_count: 0,
        dimensions: [],
        object_classes: [],
        interaction_classes: [],
        datatype_names: [],
        object_nodes: [],
        interaction_nodes: [],
        validation_command: customLoadSetCommand(row.name, row.member_ids),
        validation_json_path: null,
        validation_md_path: null,
        validation_html_path: null,
        edition_classes: editionClasses,
        baseline_kinds: baselineKinds,
        load_mode: "browser-saved",
        source_kind: "browser-saved-custom-load-set",
      }};
    }}

    function customLoadSets() {{
      return [
        ...snapshot.custom_load_sets.map((loadSet) => ({{ ...loadSet, source_kind: "snapshot-custom-load-set" }})),
        ...browserCustomLoadSets.map(hydratedBrowserLoadSet),
      ];
    }}

    function currentCatalogItems() {{
      return selectedCatalogKind === "custom-load-set" ? customLoadSets() : snapshot.families;
    }}

    function currentCatalogItem() {{
      if (selectedCatalogKind === "custom-load-set") return customLoadSets().find((loadSet) => loadSet.name === selectedCatalogName) || null;
      return familyMap.get(selectedCatalogName) || null;
    }}

    function catalogSearchText(family) {{
      return [
        family.scenario_family || family.name,
        (family.edition_classes || []).join(" "),
        (family.baseline_kinds || []).join(" "),
        family.load_mode,
        family.member_ids.join(" "),
      ].join(" ").toLowerCase();
    }}

    function renderFamilyList() {{
      const filter = document.getElementById("family-filter").value.trim().toLowerCase();
      const host = document.getElementById("family-list");
      host.innerHTML = "";
      for (const family of currentCatalogItems()) {{
        const catalogName = family.scenario_family || family.name;
        if (filter && !catalogSearchText(family).includes(filter)) continue;
        const card = document.createElement("div");
        card.className = "family-card" + (catalogName === selectedCatalogName ? " active" : "");
        card.innerHTML = `
          <strong>${{catalogName}}</strong><br>
          <span class="muted">${{(family.edition_classes || ["custom"]).join(", ")}} | ${{family.load_mode}}</span><br>
          <span class="muted">${{family.object_class_count}} objects, ${{family.interaction_class_count}} interactions, ${{family.datatype_count}} datatypes</span>
        `;
        card.onclick = () => {{
          selectedCatalogName = catalogName;
          selectedNodeName = null;
          renderFamilyList();
          renderInspect();
          renderSearch();
        }};
        host.appendChild(card);
      }}
    }}

    function renderInspect() {{
      const family = currentCatalogItem();
      const host = document.getElementById("inspect-panel");
      if (!family) {{
        host.textContent = "Select a family or custom load set.";
        return;
      }}
      const title = family.scenario_family || family.name;
      host.innerHTML = `
        <dl class="kv">
          <dt>Selection</dt><dd>${{title}}</dd>
          <dt>Edition classes</dt><dd>${{(family.edition_classes || ["custom"]).join(", ")}}</dd>
          <dt>Baseline kinds</dt><dd>${{(family.baseline_kinds || ["custom"]).join(", ")}}</dd>
          <dt>Load mode</dt><dd>${{family.load_mode}}</dd>
          <dt>Parse status</dt><dd>${{family.parse_status}}${{family.parse_error ? `: ${{family.parse_error}}` : ""}}</dd>
          <dt>Default load set</dt><dd>${{(family.default_load_set_ids || family.member_ids).join(", ")}}</dd>
          <dt>Module names</dt><dd>${{family.module_names.join(", ")}}</dd>
          <dt>Dimensions</dt><dd>${{family.dimensions.join(", ") || "n/a"}}</dd>
        </dl>
        <h3>Validation Packet</h3>
        <div class="list">
          <code>${{family.validation_command || "n/a"}}</code>
          ${{
            family.validation_html_path
              ? `<a href="${{family.validation_html_path}}" target="_blank" rel="noopener">open HTML validation packet</a><br>
                 <a href="${{family.validation_md_path}}" target="_blank" rel="noopener">open Markdown validation packet</a><br>
                 <a href="${{family.validation_json_path}}" target="_blank" rel="noopener">open JSON validation packet</a>`
              : `<span class="muted">Validation packet not generated for this snapshot.</span>`
          }}
        </div>
        <h3>Member Paths</h3>
        <div class="list">${{family.member_paths.map((item) => `<code>${{item}}</code>`).join("")}}</div>
      `;
      renderTree();
      renderEditFlow();
    }}

    function renderSearch() {{
      const filter = document.getElementById("search-filter").value.trim().toLowerCase();
      const tbody = document.getElementById("search-results");
      const rows = snapshot.search_index.filter((row) => {{
        if (selectedCatalogName && row.source_name !== selectedCatalogName) return false;
        if (!filter) return true;
        return [row.kind, row.name, row.source_name, row.parent_name || "", row.lineage.join(" "), row.edition_classes.join(" ")].join(" ").toLowerCase().includes(filter);
      }}).slice(0, 250);
      tbody.innerHTML = rows.map((row) => `
        <tr>
          <td>${{row.kind}}</td>
          <td><code>${{row.name}}</code><br><span class="muted">${{row.lineage.join(" > ")}}</span></td>
          <td>${{row.source_name}}</td>
        </tr>
      `).join("");
    }}

    function currentNodes() {{
      const family = currentCatalogItem();
      if (!family) return [];
      const kind = document.getElementById("tree-kind").value;
      return kind === "interaction" ? family.interaction_nodes : family.object_nodes;
    }}

    function renderTree() {{
      const family = currentCatalogItem();
      const panel = document.getElementById("tree-panel");
      if (!family) {{
        panel.innerHTML = "";
        return;
      }}
      const filter = document.getElementById("tree-filter").value.trim().toLowerCase();
      const rows = currentNodes().filter((row) => {{
        if (!filter) return true;
        return [row.full_name, row.parent_name || "", row.lineage.join(" "), row.datatype_hints.join(" ")].join(" ").toLowerCase().includes(filter);
      }});
      panel.innerHTML = rows.map((row) => {{
        const depth = Math.max(0, row.lineage.length - 1) * 16;
        const active = row.full_name === selectedNodeName ? " active" : "";
        return `<div class="tree-row${{active}}" data-name="${{row.full_name}}" style="padding-left:${{depth}}px">
          <strong>${{row.full_name.split(".").slice(-1)[0]}}</strong>
          <span class="muted">(${{row.declared_count}}/${{row.total_count}})</span><br>
          <span class="muted">${{row.full_name}}</span>
        </div>`;
      }}).join("");
      panel.querySelectorAll(".tree-row").forEach((element) => {{
        element.onclick = () => {{
          selectedNodeName = element.dataset.name;
          renderTree();
          renderNodePanel();
        }};
      }});
      if (!selectedNodeName && rows[0]) selectedNodeName = rows[0].full_name;
      renderNodePanel();
    }}

    function renderNodePanel() {{
      const host = document.getElementById("node-panel");
      const row = currentNodes().find((item) => item.full_name === selectedNodeName);
      if (!row) {{
        host.innerHTML = `<span class="muted">Select a node.</span>`;
        return;
      }}
      host.innerHTML = `
        <h3>Node Drill-Down</h3>
        <dl class="kv">
          <dt>Full name</dt><dd><code>${{row.full_name}}</code></dd>
          <dt>Parent</dt><dd>${{row.parent_name || "n/a"}}</dd>
          <dt>Lineage</dt><dd>${{row.lineage.join(" > ")}}</dd>
          <dt>Declared</dt><dd>${{row.declared_names.join(", ") || "n/a"}}</dd>
          <dt>Available</dt><dd>${{row.total_names.join(", ") || "n/a"}}</dd>
          <dt>Datatype hints</dt><dd>${{row.datatype_hints.join(", ") || "n/a"}}</dd>
          <dt>Leaf</dt><dd>${{String(row.is_leaf)}}</dd>
        </dl>
      `;
    }}

    function renderEditFlow() {{
      const family = currentCatalogItem();
      const summary = document.getElementById("edit-summary");
      const command = document.getElementById("edit-command");
      if (!family) {{
        summary.textContent = "Select a family or custom load set.";
        command.innerHTML = "";
        return;
      }}
      const editable = snapshot.entries.filter((entry) => family.member_ids.includes(entry.id) && entry.baseline_kind === "repo-owned");
      const blocked = snapshot.entries.filter((entry) => family.member_ids.includes(entry.id) && entry.baseline_kind !== "repo-owned");
      if (!editable.length) {{
        summary.textContent = `No repo-owned entries in this family. Third-party members are read-only.`;
      }} else {{
        summary.textContent = `Repo-owned editable entries: ${{editable.map((entry) => entry.id).join(", ")}}. Third-party members remain read-only.`;
      }}
      if (blocked.length) {{
        summary.textContent += ` Blocked: ${{blocked.map((entry) => entry.id).join(", ")}}`;
      }}
      const firstEditable = editable[0];
      if (!firstEditable) {{
        command.innerHTML = "<span class='muted'>No guarded edit command available for this selection.</span>";
        return;
      }}
      const desc = document.getElementById("edit-description").value.trim();
      const keywords = document.getElementById("edit-keywords").value.trim();
      const notes = document.getElementById("edit-notes").value.trim();
      let cmd = `./tools/fom-workbench --edit-entry ${{firstEditable.id}}`;
      if (desc) cmd += ` --set-description ${{JSON.stringify(desc)}}`;
      for (const item of keywords.split(",").map((value) => value.trim()).filter(Boolean)) cmd += ` --add-keyword ${{JSON.stringify(item)}}`;
      for (const item of notes.split(",").map((value) => value.trim()).filter(Boolean)) cmd += ` --add-note ${{JSON.stringify(item)}}`;
      command.innerHTML = `<code>${{cmd}}</code>`;
    }}

    function renderBuilder() {{
      const nameBox = document.getElementById("builder-name");
      const filter = document.getElementById("builder-filter").value.trim().toLowerCase();
      const listHost = document.getElementById("builder-entry-list");
      const savedHost = document.getElementById("builder-saved");
      const commandHost = document.getElementById("builder-command");
      const rows = snapshot.entries.filter((entry) => {{
        if (!filter) return true;
        return [entry.id, entry.scenario_family, entry.edition_class, entry.path, entry.load_mode, entry.baseline_kind]
          .join(" ")
          .toLowerCase()
          .includes(filter);
      }});
      listHost.innerHTML = rows.map((entry) => {{
        const checked = builderSelectedMemberIds.has(entry.id) ? "checked" : "";
        return `<label><input type="checkbox" data-entry-id="${{entry.id}}" ${{checked}}> <code>${{entry.id}}</code> <span class="muted">${{entry.scenario_family}} | ${{entry.edition_class}} | ${{entry.load_mode}}</span></label>`;
      }}).join("");
      listHost.querySelectorAll("input[type=checkbox]").forEach((node) => {{
        node.addEventListener("change", () => {{
          if (node.checked) builderSelectedMemberIds.add(node.dataset.entryId);
          else builderSelectedMemberIds.delete(node.dataset.entryId);
          renderBuilder();
        }});
      }});
      const selectedIds = [...builderSelectedMemberIds].sort();
      const candidateName = nameBox.value.trim();
      if (!selectedIds.length) {{
        commandHost.innerHTML = "<span class='muted'>Select one or more baseline entries to build a named custom load set.</span>";
      }} else if (!candidateName) {{
        commandHost.innerHTML = `<code>${{customLoadSetCommand("custom-name", selectedIds)}}</code>`;
      }} else {{
        commandHost.innerHTML = `<code>${{customLoadSetCommand(candidateName, selectedIds)}}</code>`;
      }}
      if (!browserCustomLoadSets.length) {{
        savedHost.innerHTML = "<span class='muted'>No browser-saved custom load sets yet.</span>";
        return;
      }}
      savedHost.innerHTML = browserCustomLoadSets.map((row) => `
        <div style="margin-bottom: 10px;">
          <strong>${{row.name}}</strong><br>
          <span class="muted">${{row.member_ids.join(", ")}}</span><br>
          <button type="button" data-action="load" data-name="${{row.name}}">load selection</button>
          <button type="button" data-action="inspect" data-name="${{row.name}}">inspect</button>
          <button type="button" data-action="delete" data-name="${{row.name}}">delete</button>
        </div>
      `).join("");
      savedHost.querySelectorAll("button").forEach((button) => {{
        button.addEventListener("click", () => {{
          const row = browserCustomLoadSets.find((item) => item.name === button.dataset.name);
          if (!row) return;
          if (button.dataset.action === "load") {{
            document.getElementById("builder-name").value = row.name;
            builderSelectedMemberIds = new Set(row.member_ids);
            renderBuilder();
            return;
          }}
          if (button.dataset.action === "inspect") {{
            document.getElementById("catalog-mode").value = "custom-load-set";
            selectedCatalogKind = "custom-load-set";
            selectedCatalogName = row.name;
            selectedNodeName = null;
            renderFamilyList();
            renderInspect();
            renderSearch();
            setDiffSelectors();
            renderDiff();
            return;
          }}
          browserCustomLoadSets = browserCustomLoadSets.filter((item) => item.name !== row.name);
          saveBrowserCustomLoadSets();
          if (selectedCatalogKind === "custom-load-set" && selectedCatalogName === row.name) {{
            selectedCatalogName = customLoadSets()[0]?.name || null;
          }}
          renderBuilder();
          renderFamilyList();
          renderInspect();
          renderSearch();
          setDiffSelectors();
          renderDiff();
        }});
      }});
    }}

    function saveBuilderSelection() {{
      const name = document.getElementById("builder-name").value.trim();
      const memberIds = [...builderSelectedMemberIds].sort();
      const commandHost = document.getElementById("builder-command");
      if (!name) {{
        commandHost.innerHTML = "<span class='muted'>Name the custom load set before saving it in the browser.</span>";
        return;
      }}
      if (!memberIds.length) {{
        commandHost.innerHTML = "<span class='muted'>Select at least one baseline entry before saving a custom load set.</span>";
        return;
      }}
      if (fixedFamilyNames.has(name) || fixedCustomLoadSetNames.has(name)) {{
        commandHost.innerHTML = `<span class='muted'>${{name}} is already used by a family or generated custom load set. Pick another name.</span>`;
        return;
      }}
      browserCustomLoadSets = browserCustomLoadSets.filter((row) => row.name !== name);
      browserCustomLoadSets.push({{ name, member_ids: memberIds }});
      browserCustomLoadSets.sort((left, right) => left.name.localeCompare(right.name));
      saveBrowserCustomLoadSets();
      selectedCatalogKind = "custom-load-set";
      selectedCatalogName = name;
      selectedNodeName = null;
      renderBuilder();
      renderFamilyList();
      renderInspect();
      renderSearch();
      setDiffSelectors();
      renderDiff();
    }}

    function exportBuilderSets() {{
      const transfer = document.getElementById("builder-transfer");
      const commandHost = document.getElementById("builder-command");
      if (!browserCustomLoadSets.length) {{
        commandHost.innerHTML = "<span class='muted'>No browser-saved custom load sets to export.</span>";
        return;
      }}
      const payload = JSON.stringify(browserCustomLoadSets, null, 2);
      transfer.value = payload;
      if (window.URL && window.Blob) {{
        const blob = new Blob([payload], {{ type: "application/json" }});
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "hla2010-fom-workbench-custom-load-sets.json";
        link.click();
        URL.revokeObjectURL(url);
      }}
      commandHost.innerHTML = "<span class='muted'>Exported browser-saved custom load sets to the transfer box and download prompt.</span>";
    }}

    function importBuilderSets() {{
      const transfer = document.getElementById("builder-transfer");
      const commandHost = document.getElementById("builder-command");
      const raw = transfer.value.trim();
      if (!raw) {{
        commandHost.innerHTML = "<span class='muted'>Paste exported custom load set JSON into the transfer box before importing.</span>";
        return;
      }}
      let parsed;
      try {{
        parsed = JSON.parse(raw);
      }} catch (_error) {{
        commandHost.innerHTML = "<span class='muted'>Import JSON is malformed.</span>";
        return;
      }}
      const imported = normalizeBrowserCustomLoadSets(parsed);
      if (!imported.length) {{
        commandHost.innerHTML = "<span class='muted'>Import JSON did not contain any valid browser custom load sets.</span>";
        return;
      }}
      const merged = new Map(browserCustomLoadSets.map((row) => [row.name, row]));
      for (const row of imported) merged.set(row.name, row);
      browserCustomLoadSets = [...merged.values()].sort((left, right) => left.name.localeCompare(right.name));
      saveBrowserCustomLoadSets();
      renderBuilder();
      renderFamilyList();
      renderInspect();
      renderSearch();
      setDiffSelectors();
      renderDiff();
      commandHost.innerHTML = `<span class='muted'>Imported ${{imported.length}} browser custom load set(s).</span>`;
    }}

    function diffKey(left, right) {{
      return `${{left}}::${{right}}`;
    }}

    function setDiffSelectors() {{
      const left = document.getElementById("left-family");
      const right = document.getElementById("right-family");
      const options = [
        ...snapshot.families.map((family) => family.scenario_family),
        ...customLoadSets().map((loadSet) => loadSet.name),
      ].map((name) => `<option value="${{name}}">${{name}}</option>`).join("");
      left.innerHTML = options;
      right.innerHTML = options;
      left.value = snapshot.families[0]?.scenario_family || "";
      right.value = customLoadSets()[0]?.name || snapshot.families[1]?.scenario_family || snapshot.families[0]?.scenario_family || "";
      left.onchange = renderDiff;
      right.onchange = renderDiff;
    }}

    function loadSetByName(name) {{
      return customLoadSets().find((row) => row.name === name) || null;
    }}

    function renderDiff() {{
      const left = document.getElementById("left-family").value;
      const right = document.getElementById("right-family").value;
      const host = document.getElementById("diff-panel");
      const customLeft = document.getElementById("custom-left").value.trim();
      const customRight = document.getElementById("custom-right").value.trim();
      if (customLeft || customRight) {{
        host.innerHTML = `<p class="muted">Custom load-set diffing is generated by the tool with named sets. Example:</p><div class="list"><code>./tools/fom-workbench --html --custom-load-set custom-left=${{customLeft}} --custom-load-set custom-right=${{customRight}} --diff custom-left:custom-right</code></div>`;
        return;
      }}
      if (!left || !right || left === right) {{
        host.textContent = "Select two distinct families to compare.";
        return;
      }}
      const diff = diffMap.get(diffKey(left, right)) || diffMap.get(diffKey(right, left));
      if (!diff) {{
        const leftLoadSet = loadSetByName(left);
        const rightLoadSet = loadSetByName(right);
        if (leftLoadSet || rightLoadSet) {{
          const leftCommand = leftLoadSet ? customLoadSetCommand(leftLoadSet.name, leftLoadSet.member_ids) : null;
          const rightCommand = rightLoadSet ? customLoadSetCommand(rightLoadSet.name, rightLoadSet.member_ids) : null;
          host.innerHTML = `
            <p class="muted">No precomputed diff row is available for this pair in the current snapshot.</p>
            <div class="list">
              ${{
                leftCommand ? `<code>${{leftCommand}}</code>` : ""
              }}
              ${{
                rightCommand ? `<code>${{rightCommand}}</code>` : ""
              }}
              <code>./tools/fom-workbench --html${{leftLoadSet ? ` --custom-load-set ${{leftLoadSet.name}}=${{leftLoadSet.member_ids.join(",")}}` : ""}}${{rightLoadSet ? ` --custom-load-set ${{rightLoadSet.name}}=${{rightLoadSet.member_ids.join(",")}}` : ""}} --diff ${{left}}:${{right}}</code>
            </div>
          `;
          return;
        }}
        host.textContent = "No diff row available.";
        return;
      }}
      const leftLoadSet = loadSetByName(left);
      const rightLoadSet = loadSetByName(right);
      if (!diff.comparable) {{
        host.textContent = `Not comparable: ${{diff.reason || "unknown"}}`;
        return;
      }}
      host.innerHTML = `
        <p><strong>${{diff.left_family}}</strong> vs <strong>${{diff.right_family}}</strong></p>
        <p class="muted">${{diff.left_kind}} vs ${{diff.right_kind}} | left members: ${{diff.left_member_ids.join(", ")}} | right members: ${{diff.right_member_ids.join(", ")}}</p>
        ${{
          leftLoadSet || rightLoadSet
            ? `<div class="list">
                 ${{
                   leftLoadSet && leftLoadSet.validation_html_path
                     ? `<a href="${{leftLoadSet.validation_html_path}}" target="_blank" rel="noopener">open ${{leftLoadSet.name}} validation packet</a><br>`
                     : ""
                 }}
                 ${{
                   rightLoadSet && rightLoadSet.validation_html_path
                     ? `<a href="${{rightLoadSet.validation_html_path}}" target="_blank" rel="noopener">open ${{rightLoadSet.name}} validation packet</a>`
                     : ""
                 }}
               </div>`
            : ""
        }}
        <div class="split">
          <div>
            <h3>Only Left Objects</h3>
            <div class="list">${{diff.only_left_object_classes.slice(0, 120).map((item) => `<code>${{item}}</code>`).join("") || "<span class='muted'>none</span>"}}</div>
          </div>
          <div>
            <h3>Only Right Objects</h3>
            <div class="list">${{diff.only_right_object_classes.slice(0, 120).map((item) => `<code>${{item}}</code>`).join("") || "<span class='muted'>none</span>"}}</div>
          </div>
        </div>
        <div class="split" style="margin-top: 14px;">
          <div>
            <h3>Only Left Interactions</h3>
            <div class="list">${{diff.only_left_interaction_classes.slice(0, 120).map((item) => `<code>${{item}}</code>`).join("") || "<span class='muted'>none</span>"}}</div>
          </div>
          <div>
            <h3>Only Right Interactions</h3>
            <div class="list">${{diff.only_right_interaction_classes.slice(0, 120).map((item) => `<code>${{item}}</code>`).join("") || "<span class='muted'>none</span>"}}</div>
          </div>
        </div>
      `;
    }}

    document.getElementById("family-filter").addEventListener("input", renderFamilyList);
    document.getElementById("catalog-mode").addEventListener("change", (event) => {{
      selectedCatalogKind = event.target.value;
      selectedCatalogName = selectedCatalogKind === "custom-load-set"
        ? (customLoadSets()[0]?.name || null)
        : (snapshot.families[0]?.scenario_family || null);
      selectedNodeName = null;
      renderFamilyList();
      renderInspect();
      renderSearch();
    }});
    document.getElementById("search-filter").addEventListener("input", renderSearch);
    document.getElementById("tree-filter").addEventListener("input", renderTree);
    document.getElementById("tree-kind").addEventListener("change", () => {{ selectedNodeName = null; renderTree(); }});
    document.getElementById("edit-description").addEventListener("input", renderEditFlow);
    document.getElementById("edit-keywords").addEventListener("input", renderEditFlow);
    document.getElementById("edit-notes").addEventListener("input", renderEditFlow);
    document.getElementById("builder-filter").addEventListener("input", renderBuilder);
    document.getElementById("builder-name").addEventListener("input", renderBuilder);
    document.getElementById("builder-save").addEventListener("click", saveBuilderSelection);
    document.getElementById("builder-clear").addEventListener("click", () => {{
      builderSelectedMemberIds = new Set();
      document.getElementById("builder-name").value = "";
      renderBuilder();
    }});
    document.getElementById("builder-export").addEventListener("click", exportBuilderSets);
    document.getElementById("builder-import").addEventListener("click", importBuilderSets);
    document.getElementById("custom-left").addEventListener("input", renderDiff);
    document.getElementById("custom-right").addEventListener("input", renderDiff);
    setCapabilities();
    renderBuilder();
    renderFamilyList();
    renderInspect();
    renderSearch();
    setDiffSelectors();
    renderDiff();
  </script>
</body>
</html>"""


def write_fom_workbench_html(
    *,
    output_dir: str | Path,
    custom_load_sets: Mapping[str, tuple[str, ...]] | None = None,
    diff_specs: tuple[tuple[str, str], ...] = (),
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    validation_output_dir = output_path / "validation_packets"
    snapshot = build_fom_workbench_snapshot(
        custom_load_sets=custom_load_sets,
        diff_specs=diff_specs,
        validation_output_dir=validation_output_dir,
    )
    html_path = output_path / "fom_workbench.html"
    html_path.write_text(_render_workbench_html(snapshot), encoding="utf-8")
    return html_path


__all__ = [
    "FOMWorkbenchDiff",
    "FOMWorkbenchFamily",
    "FOMWorkbenchSearchRow",
    "FOMWorkbenchSnapshot",
    "build_fom_workbench_snapshot",
    "write_fom_workbench_html",
    "write_fom_workbench_snapshot",
]
