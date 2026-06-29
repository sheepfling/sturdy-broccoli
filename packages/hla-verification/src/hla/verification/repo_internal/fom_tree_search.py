"""Shared FOM tree, search, and loaded-set helpers."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote

from hla.verification.repo_internal.fom_corpus_classification import classify_edition_scope
from hla.verification.repo_internal.fom_inventory import (
    FOMInventoryRecord,
    default_load_set_records,
    lookup_fom_inventory,
)


@dataclass(frozen=True, slots=True)
class FOMTreeNode:
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
class FOMSearchRow:
    source_name: str
    source_kind: str
    kind: str
    name: str
    parent_name: str | None
    lineage: tuple[str, ...]
    is_leaf: bool
    edition_classes: tuple[str, ...]
    edition_scope: str
    baseline_kinds: tuple[str, ...]
    load_mode: str


def _edition_scope_for_records(records: tuple[FOMInventoryRecord, ...]) -> str:
    scopes = {classify_edition_scope(record) for record in records}
    if not scopes:
        return "schema-only / support-only"
    if scopes == {"schema-only / support-only"}:
        return "schema-only / support-only"
    if len(scopes) == 1:
        return next(iter(scopes))
    if scopes <= {"2010 only", "2025 only"}:
        return "cross-edition / ambiguous"
    if "cross-edition / ambiguous" in scopes:
        return "cross-edition / ambiguous"
    if "schema-only / support-only" in scopes and len(scopes) > 1:
        return "cross-edition / ambiguous"
    return "cross-edition / ambiguous"


def _spec_datatype_hints(spec: Any) -> tuple[str, ...]:
    datatype_map = getattr(spec, "attribute_datatypes", None) or getattr(spec, "parameter_datatypes", None) or {}
    hints: list[str] = []
    for value in datatype_map.values():
        if value and value not in hints:
            hints.append(value)
    return tuple(hints)


def build_fom_tree_nodes(specs: Iterable[Any], *, kind: str) -> tuple[FOMTreeNode, ...]:
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

    rows: list[FOMTreeNode] = []
    for spec in sorted(specs, key=lambda item: item.full_name):
        declared_names = tuple(spec.declared_attributes) if kind == "object" else tuple(spec.declared_parameters)
        total_names = tuple(spec.attributes) if kind == "object" else tuple(spec.parameters)
        rows.append(
            FOMTreeNode(
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


def build_fom_search_rows(
    *,
    source_name: str,
    source_kind: str,
    object_nodes: Iterable[FOMTreeNode] = (),
    interaction_nodes: Iterable[FOMTreeNode] = (),
    datatype_names: Iterable[str] = (),
    edition_classes: Iterable[str] = (),
    edition_scope: str,
    baseline_kinds: Iterable[str] = (),
    load_mode: str,
) -> tuple[FOMSearchRow, ...]:
    rows: list[FOMSearchRow] = []
    normalized_edition_classes = tuple(edition_classes)
    normalized_baseline_kinds = tuple(baseline_kinds)
    for node in object_nodes:
        rows.append(
            FOMSearchRow(
                source_name=source_name,
                source_kind=source_kind,
                kind="object",
                name=node.full_name,
                parent_name=node.parent_name,
                lineage=node.lineage,
                is_leaf=node.is_leaf,
                edition_classes=normalized_edition_classes,
                edition_scope=edition_scope,
                baseline_kinds=normalized_baseline_kinds,
                load_mode=load_mode,
            )
        )
    for node in interaction_nodes:
        rows.append(
            FOMSearchRow(
                source_name=source_name,
                source_kind=source_kind,
                kind="interaction",
                name=node.full_name,
                parent_name=node.parent_name,
                lineage=node.lineage,
                is_leaf=node.is_leaf,
                edition_classes=normalized_edition_classes,
                edition_scope=edition_scope,
                baseline_kinds=normalized_baseline_kinds,
                load_mode=load_mode,
            )
        )
    for name in sorted(datatype_names):
        rows.append(
            FOMSearchRow(
                source_name=source_name,
                source_kind=source_kind,
                kind="datatype",
                name=name,
                parent_name=None,
                lineage=(name,),
                is_leaf=True,
                edition_classes=normalized_edition_classes,
                edition_scope=edition_scope,
                baseline_kinds=normalized_baseline_kinds,
                load_mode=load_mode,
            )
        )
    return tuple(sorted(rows, key=lambda row: (row.source_name, row.kind, row.name)))


def describe_loaded_fom_modules(
    modules: Iterable[str | Path | Any],
    *,
    year: int | None = None,
) -> dict[str, Any] | None:
    records: list[FOMInventoryRecord] = []
    seen_ids: set[str] = set()
    for module in modules:
        record = lookup_fom_inventory(module, year=year)
        if record is None or record.id in seen_ids:
            continue
        seen_ids.add(record.id)
        records.append(record)
    if not records:
        return None

    grouped: dict[str, list[FOMInventoryRecord]] = defaultdict(list)
    for record in records:
        grouped[record.scenario_family].append(record)

    edition_classes = tuple(sorted(dict.fromkeys(record.edition_class for record in records)))
    baseline_kinds = tuple(sorted(dict.fromkeys(record.baseline_kind for record in records)))
    load_modes = tuple(sorted(dict.fromkeys(record.load_mode for record in records)))
    scenario_families = tuple(sorted(grouped))
    workbench_targets = [
        {
            "label": f"Open {family} in workbench",
            "target_kind": "family",
            "target_name": family,
            "fragment": f"#family={quote(family)}",
        }
        for family in scenario_families
    ]
    default_load_sets = [
        {
            "scenario_family": family,
            "member_ids": [record.id for record in default_load_set_records(tuple(grouped[family]))],
            "member_paths": [record.path for record in default_load_set_records(tuple(grouped[family]))],
        }
        for family in scenario_families
    ]
    return {
        "record_ids": [record.id for record in records],
        "member_paths": [record.path for record in records],
        "scenario_families": list(scenario_families),
        "edition_classes": list(edition_classes),
        "edition_scope": _edition_scope_for_records(tuple(records)),
        "baseline_kinds": list(baseline_kinds),
        "load_modes": list(load_modes),
        "default_load_sets": default_load_sets,
        "workbench_targets": workbench_targets,
    }


__all__ = [
    "FOMSearchRow",
    "FOMTreeNode",
    "build_fom_search_rows",
    "build_fom_tree_nodes",
    "describe_loaded_fom_modules",
]
