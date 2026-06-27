"""Snapshot helpers for a future FOM workbench UI."""

from __future__ import annotations

import ast
import html
import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from hla.fom import FOMCatalog, FOMMergeError, FOMResolutionError, FOMResolver, merge_fom_modules
from hla.verification.repo_internal.fom_inventory import FOMInventoryRecord, default_load_set_records, inventory_records
from hla.verification.repo_internal.fom_corpus_classification import classify_edition_scope
from hla.verification.repo_internal.fom_tree_search import (
    FOMSearchRow as FOMWorkbenchSearchRow,
    FOMTreeNode as FOMWorkbenchNode,
    build_fom_search_rows,
    build_fom_tree_nodes,
)
from hla.verification.repo_internal.fom_validate import write_fom_validation, write_fom_validation_html
from hla.verification.repo_internal.siso_corpus import is_default_scope_record


@dataclass(frozen=True, slots=True)
class FOMWorkbenchFamily:
    scenario_family: str
    edition_classes: tuple[str, ...]
    edition_scope: str
    baseline_kinds: tuple[str, ...]
    load_mode: str
    member_ids: tuple[str, ...]
    member_paths: tuple[str, ...]
    default_load_set_ids: tuple[str, ...]
    default_load_set_paths: tuple[str, ...]
    parse_status: str
    parse_error_kind: str | None
    parse_error: str | None
    recommended_next_step: str
    merge_conflict_kind: str | None
    merge_conflict_symbol: str | None
    merge_conflict_members: tuple[str, ...]
    merge_conflict_member_details: tuple[dict[str, Any], ...]
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
    catalog_status: str = "ok"
    validation_verdict: str | None = None
    validation_passed: bool | None = None
    validation_issue_count: int = 0
    validation_issue_layers: tuple[str, ...] = ()
    validation_issue_groups: tuple[dict[str, Any], ...] = ()
    datatype_normalizations: tuple[dict[str, str], ...] = ()
    resolved: tuple[Any, ...] = ()


@dataclass(frozen=True, slots=True)
class FOMWorkbenchLoadSet:
    name: str
    member_ids: tuple[str, ...]
    member_paths: tuple[str, ...]
    edition_scope: str
    parse_status: str
    parse_error_kind: str | None
    parse_error: str | None
    recommended_next_step: str
    merge_conflict_kind: str | None
    merge_conflict_symbol: str | None
    merge_conflict_members: tuple[str, ...]
    merge_conflict_member_details: tuple[dict[str, Any], ...]
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
    catalog_status: str = "ok"
    validation_verdict: str | None = None
    validation_passed: bool | None = None
    validation_issue_count: int = 0
    validation_issue_layers: tuple[str, ...] = ()
    validation_issue_groups: tuple[dict[str, Any], ...] = ()
    datatype_normalizations: tuple[dict[str, str], ...] = ()
    resolved: tuple[Any, ...] = ()

@dataclass(frozen=True, slots=True)
class FOMWorkbenchDiff:
    left_family: str
    right_family: str
    comparable: bool
    reason: str | None
    left_parse_status: str
    right_parse_status: str
    left_parse_error_kind: str | None
    right_parse_error_kind: str | None
    left_parse_error: str | None
    right_parse_error: str | None
    left_recommended_next_step: str | None
    right_recommended_next_step: str | None
    left_merge_conflict_kind: str | None
    right_merge_conflict_kind: str | None
    left_merge_conflict_symbol: str | None
    right_merge_conflict_symbol: str | None
    left_merge_conflict_members: tuple[str, ...]
    right_merge_conflict_members: tuple[str, ...]
    left_merge_conflict_member_details: tuple[dict[str, Any], ...]
    right_merge_conflict_member_details: tuple[dict[str, Any], ...]
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
        "edition_scope": classify_edition_scope(record),
        "load_mode": record.load_mode,
        "baseline_kind": record.baseline_kind,
        "scenario_family": record.scenario_family,
        "notes": record.notes,
    }


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


def _node_rows(specs: Iterable[Any], *, kind: str) -> tuple[FOMWorkbenchNode, ...]:
    return tuple(build_fom_tree_nodes(specs, kind=kind))


def _default_load_set(records: tuple[FOMInventoryRecord, ...]) -> tuple[FOMInventoryRecord, ...]:
    return default_load_set_records(records)


def _resolve_catalog(records: tuple[FOMInventoryRecord, ...]) -> tuple[tuple[str, ...], FOMCatalog]:
    resolver = FOMResolver()
    resolved = resolver.resolve_many(tuple((_repo_root() / record.path) for record in records))
    catalog = merge_fom_modules(resolved)
    module_names = tuple(module.name or str(module.source) for module in resolved)
    return module_names, catalog


def _safe_literal(value: str) -> Any:
    try:
        return ast.literal_eval(value)
    except Exception:
        return value


def _member_label(name: str | None, source: object) -> str:
    return str(name or source or "unknown-member")


def _record_by_source(
    records: tuple[FOMInventoryRecord, ...],
) -> dict[str, FOMInventoryRecord]:
    return {str((_repo_root() / record.path).resolve()): record for record in records}


def _detail_base(module: Any, records_by_source: Mapping[str, FOMInventoryRecord]) -> dict[str, Any]:
    source_path = str(Path(str(module.source)).resolve())
    record = records_by_source.get(source_path)
    return {
        "member": _member_label(module.name, module.source),
        "entry_id": record.id if record else None,
        "entry_path": record.path if record else None,
        "baseline_kind": record.baseline_kind if record else None,
    }


def _merge_conflict_from_modules(
    message: str,
    resolved_modules: tuple[Any, ...],
    records: tuple[FOMInventoryRecord, ...],
) -> tuple[str | None, str | None, tuple[str, ...], tuple[dict[str, Any], ...]]:
    records_by_source = _record_by_source(records)
    definition_match = re.match(r"^Conflicting (?P<kind>.+) definition (?P<name>.+) across FOM modules$", message)
    if definition_match:
        kind = str(definition_match.group("kind"))
        symbol = str(_safe_literal(definition_match.group("name")))
        if "object class" in kind:
            details = tuple(
                {
                    **_detail_base(module, records_by_source),
                    "object_class": symbol,
                    "parent_name": next((spec.parent_name for spec in module.object_classes if spec.full_name == symbol), None),
                }
                for module in resolved_modules
                if any(spec.full_name == symbol for spec in module.object_classes)
            )
        elif "interaction class" in kind:
            details = tuple(
                {
                    **_detail_base(module, records_by_source),
                    "interaction_class": symbol,
                    "parent_name": next((spec.parent_name for spec in module.interaction_classes if spec.full_name == symbol), None),
                }
                for module in resolved_modules
                if any(spec.full_name == symbol for spec in module.interaction_classes)
            )
        elif "transportation reliability" in kind:
            details = tuple(
                {
                    **_detail_base(module, records_by_source),
                    "transportation": symbol,
                    "declaration": next(
                        (
                            {"reliable": spec.reliable, "semantics": spec.semantics}
                            for name, spec in module.transportation_specs.items()
                            if name == symbol
                        ),
                        None,
                    ),
                }
                for module in resolved_modules
                if symbol in module.transportation_names
            )
        else:
            details = tuple(
                {
                    **_detail_base(module, records_by_source),
                    "symbol": symbol,
                    "declaration": (
                        next(
                            (
                                {"category": "basic", "encoding": spec.encoding, "size": spec.size, "interpretation": spec.interpretation, "endian": spec.endian, "semantics": spec.semantics}
                                for name, spec in module.basic_datatypes.items()
                                if name == symbol
                            ),
                            None,
                        )
                        or next(
                            (
                                {"category": "simple", "representation": spec.representation, "units": spec.units, "resolution": spec.resolution, "accuracy": spec.accuracy, "semantics": spec.semantics}
                                for name, spec in module.simple_datatypes.items()
                                if name == symbol
                            ),
                            None,
                        )
                        or next(
                            (
                                {"category": "reference", "representation": spec.representation, "reference_class": spec.reference_class, "referenced_attribute": spec.referenced_attribute, "semantics": spec.semantics}
                                for name, spec in module.reference_datatypes.items()
                                if name == symbol
                            ),
                            None,
                        )
                        or next(
                            (
                                {"category": "enumerated", "representation": spec.representation, "semantics": spec.semantics}
                                for name, spec in module.enumerated_datatypes.items()
                                if name == symbol
                            ),
                            None,
                        )
                        or next(
                            (
                                {"category": "array", "data_type": spec.data_type, "cardinality": spec.cardinality, "encoding": spec.encoding, "source_encoding": spec.source_encoding, "semantics": spec.semantics}
                                for name, spec in module.array_datatypes.items()
                                if name == symbol
                            ),
                            None,
                        )
                        or next(
                            (
                                {"category": "fixed-record", "encoding": spec.encoding, "semantics": spec.semantics}
                                for name, spec in module.fixed_record_datatypes.items()
                                if name == symbol
                            ),
                            None,
                        )
                        or next(
                            (
                                {"category": "variant-record", "discriminant": spec.discriminant, "data_type": spec.data_type, "encoding": spec.encoding, "source_encoding": spec.source_encoding, "semantics": spec.semantics}
                                for name, spec in module.variant_record_datatypes.items()
                                if name == symbol
                            ),
                            None,
                        )
                        or next(
                            (
                                {"category": "update-rate", "rate": spec.rate, "semantics": spec.semantics}
                                for name, spec in module.update_rate_specs.items()
                                if name == symbol
                            ),
                            None,
                        )
                    ),
                }
                for module in resolved_modules
                if symbol in module.datatype_names or symbol in module.update_rates
            )
        return kind, symbol, tuple(detail["member"] for detail in details), details

    superclass_match = re.match(
        r"^(?P<kind>Object class|Interaction class) (?P<name>.+) has conflicting superclasses: .+$",
        message,
    )
    if superclass_match:
        symbol = str(_safe_literal(superclass_match.group("name")))
        object_kind = superclass_match.group("kind") == "Object class"
        details = tuple(
            {
                "member": _member_label(module.name, module.source),
                "symbol": symbol,
                "parent_name": next(
                    (
                        spec.parent_name
                        for spec in (module.object_classes if object_kind else module.interaction_classes)
                        if spec.full_name == symbol
                    ),
                    None,
                ),
            }
            for module in resolved_modules
            if any(
                spec.full_name == symbol
                for spec in (module.object_classes if object_kind else module.interaction_classes)
            )
        )
        return superclass_match.group("kind").lower().replace(" ", "-"), symbol, tuple(detail["member"] for detail in details), details

    logical_time_match = re.match(r"^Conflicting logical time implementations in FOM modules: (?P<values>\[.+\])$", message)
    if logical_time_match:
        values = _safe_literal(logical_time_match.group("values"))
        implementations = tuple(str(value) for value in values) if isinstance(values, (list, tuple)) else ()
        details = tuple(
            {
                "member": _member_label(module.name, module.source),
                "logical_time_implementation": getattr(module, "inferred_time_implementation", None),
            }
            for module in resolved_modules
            if getattr(module, "inferred_time_implementation", None) in implementations
        )
        return "logical-time-implementation", ", ".join(implementations), tuple(detail["member"] for detail in details), details

    return None, None, (), ()


def _workbench_failure(exc: Exception) -> tuple[str, str]:
    message = str(exc)
    if isinstance(exc, FOMMergeError):
        lowered = message.lower()
        if "conflicting logical time implementations" in lowered:
            return "merge", "Align the logical time section across the selected members, then regenerate the workbench snapshot."
        if "conflicting" in lowered and "datatype definition" in lowered:
            return "merge", "Unify the duplicate datatype definition across the selected members, then regenerate the workbench snapshot."
        if "conflicting transportation reliability definition" in lowered:
            return "merge", "Normalize the transportation reliability definition across the selected members, then regenerate the workbench snapshot."
        return "merge", "Resolve the conflicting member definitions in this selection, then regenerate the workbench snapshot."
    if isinstance(exc, FOMResolutionError):
        return "resolution", "Fix the unresolved member path or resolver mapping, then regenerate the workbench snapshot."
    return "error", "Fix the reported catalog construction failure, then regenerate the workbench snapshot."


def _validation_summary(report: Any | None) -> tuple[str | None, bool | None, int, tuple[str, ...], tuple[dict[str, Any], ...]]:
    if report is None:
        return None, None, 0, (), ()
    issues = tuple(getattr(report, "issues", ()))
    layers = tuple(sorted({issue.layer for issue in issues if getattr(issue, "layer", None)}))
    grouped: dict[str, list[str]] = defaultdict(list)
    for issue in issues:
        layer = getattr(issue, "layer", None) or "unknown"
        message = str(getattr(issue, "message", "")).strip()
        if message and message not in grouped[layer]:
            grouped[layer].append(message)
    issue_groups = tuple(
        {
            "layer": layer,
            "count": sum(1 for issue in issues if getattr(issue, "layer", None) == layer),
            "messages": tuple(messages[:3]),
        }
        for layer, messages in sorted(grouped.items())
    )
    return getattr(report, "verdict", None), getattr(report, "passed", None), len(issues), layers, issue_groups


def _catalog_status(
    *,
    parse_status: str,
    parse_error_kind: str | None,
    validation_verdict: str | None,
    validation_passed: bool | None,
) -> str:
    if parse_status == "browser-pending":
        return "browser-pending"
    if parse_status != "ok":
        return "merge-failed" if parse_error_kind == "merge" else "error"
    if validation_passed is False:
        return "validation-failed"
    if validation_verdict and validation_verdict != "conforming":
        return "warning"
    return "ok"


def _family_summary(records: tuple[FOMInventoryRecord, ...], *, validation_output_dir: Path | None = None) -> FOMWorkbenchFamily:
    load_set = _default_load_set(records)
    parse_status = "ok"
    parse_error_kind: str | None = None
    parse_error: str | None = None
    recommended_next_step = "Open the validation packet or inspect the merged tree for this family."
    merge_conflict_kind: str | None = None
    merge_conflict_symbol: str | None = None
    merge_conflict_members: tuple[str, ...] = ()
    merge_conflict_member_details: tuple[dict[str, Any], ...] = ()
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
    validation_verdict: str | None = None
    validation_passed: bool | None = None
    validation_issue_count = 0
    validation_issue_layers: tuple[str, ...] = ()
    validation_issue_groups: tuple[dict[str, Any], ...] = ()
    datatype_normalizations: tuple[dict[str, str], ...] = ()
    resolved: tuple[Any, ...] = ()
    validation_command = f"./tools/fom-validate --family {records[0].scenario_family} --html"
    try:
        resolver = FOMResolver()
        resolved = resolver.resolve_many(tuple((_repo_root() / record.path) for record in load_set))
        module_names = tuple(module.name or str(module.source) for module in resolved)
        catalog = merge_fom_modules(resolved)
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
            load_set_report = report.load_set_reports[0] if report.load_set_reports else None
            validation_verdict, validation_passed, validation_issue_count, validation_issue_layers, validation_issue_groups = _validation_summary(load_set_report)
            datatype_normalizations = tuple(getattr(load_set_report, "datatype_normalizations", ()) or ())
            validation_json_path = str((family_dir / "fom_validation_report.json").relative_to(validation_output_dir.parent))
            validation_md_path = str((family_dir / "fom_validation_report.md").relative_to(validation_output_dir.parent))
            validation_html_path = str(html_path.relative_to(validation_output_dir.parent))
    except Exception as exc:  # pragma: no cover - failure diagnostics only
        parse_status = "error"
        parse_error_kind, recommended_next_step = _workbench_failure(exc)
        parse_error = str(exc)
        if resolved and isinstance(exc, FOMMergeError):
            merge_conflict_kind, merge_conflict_symbol, merge_conflict_members, merge_conflict_member_details = _merge_conflict_from_modules(
                str(exc),
                tuple(resolved),
                load_set,
            )

    return FOMWorkbenchFamily(
        scenario_family=records[0].scenario_family,
        edition_classes=tuple(dict.fromkeys(record.edition_class for record in records)),
        edition_scope=_edition_scope_for_records(records),
        baseline_kinds=tuple(dict.fromkeys(record.baseline_kind for record in records)),
        load_mode=records[0].load_mode,
        member_ids=tuple(record.id for record in records),
        member_paths=tuple(record.path for record in records),
        default_load_set_ids=tuple(record.id for record in load_set),
        default_load_set_paths=tuple(record.path for record in load_set),
        parse_status=parse_status,
        parse_error_kind=parse_error_kind,
        parse_error=parse_error,
        recommended_next_step=recommended_next_step,
        merge_conflict_kind=merge_conflict_kind,
        merge_conflict_symbol=merge_conflict_symbol,
        merge_conflict_members=merge_conflict_members,
        merge_conflict_member_details=merge_conflict_member_details,
        catalog_status=_catalog_status(
            parse_status=parse_status,
            parse_error_kind=parse_error_kind,
            validation_verdict=validation_verdict,
            validation_passed=validation_passed,
        ),
        validation_verdict=validation_verdict,
        validation_passed=validation_passed,
        validation_issue_count=validation_issue_count,
        validation_issue_layers=validation_issue_layers,
        validation_issue_groups=validation_issue_groups,
        datatype_normalizations=datatype_normalizations,
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
    parse_error_kind: str | None = None
    parse_error: str | None = None
    recommended_next_step = "Run the validation command or inspect the merged tree for this load set."
    merge_conflict_kind: str | None = None
    merge_conflict_symbol: str | None = None
    merge_conflict_members: tuple[str, ...] = ()
    merge_conflict_member_details: tuple[dict[str, Any], ...] = ()
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
    validation_verdict: str | None = None
    validation_passed: bool | None = None
    validation_issue_count = 0
    validation_issue_layers: tuple[str, ...] = ()
    validation_issue_groups: tuple[dict[str, Any], ...] = ()
    datatype_normalizations: tuple[dict[str, str], ...] = ()
    resolved: tuple[Any, ...] = ()
    try:
        resolver = FOMResolver()
        resolved = resolver.resolve_many(tuple((_repo_root() / record.path) for record in records))
        module_names = tuple(module.name or str(module.source) for module in resolved)
        catalog = merge_fom_modules(resolved)
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
            load_set_report = report.load_set_reports[0] if report.load_set_reports else None
            validation_verdict, validation_passed, validation_issue_count, validation_issue_layers, validation_issue_groups = _validation_summary(load_set_report)
            datatype_normalizations = tuple(getattr(load_set_report, "datatype_normalizations", ()) or ())
            validation_json_path = str((load_set_dir / "fom_validation_report.json").relative_to(validation_output_dir.parent))
            validation_md_path = str((load_set_dir / "fom_validation_report.md").relative_to(validation_output_dir.parent))
            validation_html_path = str(html_path.relative_to(validation_output_dir.parent))
    except Exception as exc:  # pragma: no cover - failure diagnostics only
        parse_status = "error"
        parse_error_kind, recommended_next_step = _workbench_failure(exc)
        parse_error = str(exc)
        if resolved and isinstance(exc, FOMMergeError):
            merge_conflict_kind, merge_conflict_symbol, merge_conflict_members, merge_conflict_member_details = _merge_conflict_from_modules(
                str(exc),
                tuple(resolved),
                records,
            )
    return FOMWorkbenchLoadSet(
        name=name,
        member_ids=tuple(record.id for record in records),
        member_paths=tuple(record.path for record in records),
        edition_scope=_edition_scope_for_records(records),
        parse_status=parse_status,
        parse_error_kind=parse_error_kind,
        parse_error=parse_error,
        recommended_next_step=recommended_next_step,
        merge_conflict_kind=merge_conflict_kind,
        merge_conflict_symbol=merge_conflict_symbol,
        merge_conflict_members=merge_conflict_members,
        merge_conflict_member_details=merge_conflict_member_details,
        catalog_status=_catalog_status(
            parse_status=parse_status,
            parse_error_kind=parse_error_kind,
            validation_verdict=validation_verdict,
            validation_passed=validation_passed,
        ),
        validation_verdict=validation_verdict,
        validation_passed=validation_passed,
        validation_issue_count=validation_issue_count,
        validation_issue_layers=validation_issue_layers,
        validation_issue_groups=validation_issue_groups,
        datatype_normalizations=datatype_normalizations,
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
        rows.extend(
            build_fom_search_rows(
                source_name=family.scenario_family,
                source_kind="family",
                object_nodes=family.object_nodes,
                interaction_nodes=family.interaction_nodes,
                datatype_names=family.datatype_names,
                edition_classes=family.edition_classes,
                edition_scope=family.edition_scope,
                baseline_kinds=family.baseline_kinds,
                load_mode=family.load_mode,
            )
        )
    for load_set in custom_load_sets:
        rows.extend(
            build_fom_search_rows(
                source_name=load_set.name,
                source_kind="custom-load-set",
                object_nodes=load_set.object_nodes,
                interaction_nodes=load_set.interaction_nodes,
                datatype_names=load_set.datatype_names,
                edition_classes=(),
                edition_scope=load_set.edition_scope,
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
    left_parse_error_kind: str | None,
    right_parse_error_kind: str | None,
    left_parse_error: str | None,
    right_parse_error: str | None,
    left_recommended_next_step: str | None,
    right_recommended_next_step: str | None,
    left_merge_conflict_kind: str | None,
    right_merge_conflict_kind: str | None,
    left_merge_conflict_symbol: str | None,
    right_merge_conflict_symbol: str | None,
    left_merge_conflict_members: tuple[str, ...],
    right_merge_conflict_members: tuple[str, ...],
    left_merge_conflict_member_details: tuple[dict[str, Any], ...],
    right_merge_conflict_member_details: tuple[dict[str, Any], ...],
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
            left_parse_status=left_parse_status,
            right_parse_status=right_parse_status,
            left_parse_error_kind=left_parse_error_kind,
            right_parse_error_kind=right_parse_error_kind,
            left_parse_error=left_parse_error,
            right_parse_error=right_parse_error,
            left_recommended_next_step=left_recommended_next_step,
            right_recommended_next_step=right_recommended_next_step,
            left_merge_conflict_kind=left_merge_conflict_kind,
            right_merge_conflict_kind=right_merge_conflict_kind,
            left_merge_conflict_symbol=left_merge_conflict_symbol,
            right_merge_conflict_symbol=right_merge_conflict_symbol,
            left_merge_conflict_members=left_merge_conflict_members,
            right_merge_conflict_members=right_merge_conflict_members,
            left_merge_conflict_member_details=left_merge_conflict_member_details,
            right_merge_conflict_member_details=right_merge_conflict_member_details,
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
        left_parse_status=left_parse_status,
        right_parse_status=right_parse_status,
        left_parse_error_kind=left_parse_error_kind,
        right_parse_error_kind=right_parse_error_kind,
        left_parse_error=left_parse_error,
        right_parse_error=right_parse_error,
        left_recommended_next_step=left_recommended_next_step,
        right_recommended_next_step=right_recommended_next_step,
        left_merge_conflict_kind=left_merge_conflict_kind,
        right_merge_conflict_kind=right_merge_conflict_kind,
        left_merge_conflict_symbol=left_merge_conflict_symbol,
        right_merge_conflict_symbol=right_merge_conflict_symbol,
        left_merge_conflict_members=left_merge_conflict_members,
        right_merge_conflict_members=right_merge_conflict_members,
        left_merge_conflict_member_details=left_merge_conflict_member_details,
        right_merge_conflict_member_details=right_merge_conflict_member_details,
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
        left.parse_error_kind,
        right.parse_error_kind,
        left.parse_error,
        right.parse_error,
        left.recommended_next_step,
        right.recommended_next_step,
        left.merge_conflict_kind,
        right.merge_conflict_kind,
        left.merge_conflict_symbol,
        right.merge_conflict_symbol,
        left.merge_conflict_members,
        right.merge_conflict_members,
        left.merge_conflict_member_details,
        right.merge_conflict_member_details,
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
                    left.parse_error_kind,
                    left.parse_error,
                    left.recommended_next_step,
                    left.merge_conflict_kind,
                    left.merge_conflict_symbol,
                    left.merge_conflict_members,
                    left.merge_conflict_member_details,
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
                    left.parse_error_kind,
                    left.parse_error,
                    left.recommended_next_step,
                    left.merge_conflict_kind,
                    left.merge_conflict_symbol,
                    left.merge_conflict_members,
                    left.merge_conflict_member_details,
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
                    right.parse_error_kind,
                    right.parse_error,
                    right.recommended_next_step,
                    right.merge_conflict_kind,
                    right.merge_conflict_symbol,
                    right.merge_conflict_members,
                    right.merge_conflict_member_details,
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
                    right.parse_error_kind,
                    right.parse_error,
                    right.recommended_next_step,
                    right.merge_conflict_kind,
                    right.merge_conflict_symbol,
                    right.merge_conflict_members,
                    right.merge_conflict_member_details,
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
                    left_fields[13],
                    right_fields[13],
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
                    left_fields[6],
                    right_fields[6],
                    left_fields[7],
                    right_fields[7],
                    left_fields[8],
                    right_fields[8],
                    left_fields[9],
                    right_fields[9],
                    left_fields[10],
                    right_fields[10],
                    left_fields[11],
                    right_fields[11],
                    left_fields[12],
                    right_fields[12],
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
    records = tuple(record for record in records if is_default_scope_record(record))
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
    set_simple_datatype_representations: tuple[tuple[str, str], ...] = (),
    set_simple_datatype_semantics: tuple[tuple[str, str], ...] = (),
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

    for datatype_name, representation in set_simple_datatype_representations:
        target_node = None
        for candidate in root.findall(f".//{qname('simpleData')}"):
            name_node = next((child for child in list(candidate) if child.tag == qname("name")), None)
            if name_node is not None and (name_node.text or "").strip() == datatype_name:
                target_node = candidate
                break
        if target_node is None:
            raise ValueError(f"Simple datatype {datatype_name!r} not found in entry {entry_id!r}")
        representation_node = next((child for child in list(target_node) if child.tag == qname("representation")), None)
        if representation_node is None:
            representation_node = ET.SubElement(target_node, qname("representation"))
        representation_node.text = representation

    for datatype_name, semantics in set_simple_datatype_semantics:
        target_node = None
        for candidate in root.findall(f".//{qname('simpleData')}"):
            name_node = next((child for child in list(candidate) if child.tag == qname("name")), None)
            if name_node is not None and (name_node.text or "").strip() == datatype_name:
                target_node = candidate
                break
        if target_node is None:
            raise ValueError(f"Simple datatype {datatype_name!r} not found in entry {entry_id!r}")
        semantics_node = next((child for child in list(target_node) if child.tag == qname("semantics")), None)
        if semantics_node is None:
            semantics_node = ET.SubElement(target_node, qname("semantics"))
        semantics_node.text = semantics

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
      --bg: #f5f4ef;
      --panel: rgba(255,255,255,0.94);
      --ink: #15232c;
      --muted: #60707a;
      --line: rgba(21,35,44,0.10);
      --line-strong: rgba(21,35,44,0.18);
      --accent: #0f766e;
      --accent-soft: rgba(15,118,110,0.08);
      --healthy: #2f6b4f;
      --healthy-soft: rgba(47,107,79,0.10);
      --warning: #8b6b1e;
      --warning-soft: rgba(139,107,30,0.10);
      --danger: #8a3434;
      --danger-soft: rgba(138,52,52,0.10);
      --neutral-soft: rgba(21,35,44,0.05);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "IBM Plex Sans", "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
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
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 8px 24px rgba(21,35,44,0.04);
    }}
    h1,h2,h3 {{ margin-top: 0; }}
    .muted {{ color: var(--muted); }}
    .surface-kicker {{
      font-size: 0.78rem;
      text-transform: uppercase;
      color: var(--muted);
      letter-spacing: 0.04em;
      margin-bottom: 8px;
    }}
    .pill {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      border: 1px solid rgba(0,109,119,0.16);
      margin: 0 8px 8px 0;
      font-size: 0.82rem;
    }}
    .pill.status-ok,
    .pill.status-conforming,
    .pill.status-supported {{ background: var(--healthy-soft); color: var(--healthy); border-color: rgba(47,107,79,0.18); }}
    .pill.status-warning,
    .pill.status-blocked {{ background: var(--warning-soft); color: var(--warning); border-color: rgba(139,107,30,0.18); }}
    .pill.status-validation-failed,
    .pill.status-merge-failed,
    .pill.status-error,
    .pill.status-unsupported {{ background: var(--danger-soft); color: var(--danger); border-color: rgba(138,52,52,0.18); }}
    .pill.status-browser-pending {{ background: var(--neutral-soft); color: #42505a; border-color: rgba(16,33,43,0.16); }}
    .grid {{
      display: grid;
      grid-template-columns: 300px minmax(0, 1.25fr) 380px;
      gap: 20px;
    }}
    .workspace-stack {{
      display: grid;
      gap: 16px;
    }}
    .summary-panel {{
      padding: 18px 20px;
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(220px, 0.95fr);
      gap: 16px;
      align-items: start;
    }}
    .summary-title {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;
    }}
    .summary-title h2 {{
      overflow-wrap: anywhere;
    }}
    .summary-stats {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }}
    .stat-box {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px 14px;
      background: rgba(255,255,255,0.82);
    }}
    .stat-box.healthy {{ border-color: rgba(47,107,79,0.20); background: rgba(47,107,79,0.05); }}
    .stat-box.warning {{ border-color: rgba(139,107,30,0.20); background: rgba(139,107,30,0.05); }}
    .stat-box.failure {{ border-color: rgba(138,52,52,0.20); background: rgba(138,52,52,0.05); }}
    .stat-box.pending {{ border-color: var(--line-strong); background: var(--neutral-soft); }}
    .stat-label {{
      color: var(--muted);
      font-size: 0.82rem;
      margin-bottom: 4px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .workspace-tabs {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 14px;
    }}
    .workspace-tab {{
      padding: 8px 12px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.82);
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .workspace-tab.active {{
      background: rgba(0,109,119,0.10);
      color: var(--accent);
      border-color: rgba(0,109,119,0.18);
    }}
    .workspace-pane {{
      display: none;
    }}
    .workspace-pane.active {{
      display: block;
    }}
    .section-title {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 12px;
    }}
    .quiet-list {{
      display: grid;
      gap: 10px;
    }}
    .rail-section + .rail-section {{
      margin-top: 18px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
    }}
    input, select {{
      width: 100%;
      padding: 12px 14px;
      border-radius: 8px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.82);
      color: var(--ink);
      margin-bottom: 12px;
    }}
    button {{
      padding: 10px 14px;
      border-radius: 8px;
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
    .history-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .history-chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.82);
      color: var(--ink);
      font-size: 0.84rem;
      cursor: pointer;
    }}
    .history-chip.active {{
      border-color: var(--accent);
      color: var(--accent);
      background: var(--accent-soft);
    }}
    .focus-bar {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.62);
      padding: 10px;
      margin-bottom: 14px;
    }}
    .focus-chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 10px;
    }}
    .focus-chip {{
      padding: 7px 10px;
      border-radius: 999px;
      font-size: 0.84rem;
      color: var(--muted);
    }}
    .focus-chip.active {{
      background: var(--accent-soft);
      border-color: rgba(0,109,119,0.20);
      color: var(--accent);
    }}
    .focus-input {{
      margin-bottom: 0;
    }}
    .focus-status {{
      margin-top: 8px;
      font-size: 0.86rem;
      color: var(--muted);
    }}
    .focus-advanced {{
      margin-top: 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.72);
    }}
    .focus-advanced summary {{
      list-style: none;
      cursor: pointer;
      padding: 10px 12px;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .focus-advanced summary::-webkit-details-marker {{
      display: none;
    }}
    .focus-advanced-body {{
      padding: 0 12px 12px;
      display: grid;
      gap: 10px;
    }}
    .focus-advanced-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }}
    .focus-advanced-grid input,
    .focus-advanced-grid select {{
      margin-bottom: 0;
    }}
    .focus-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .focus-actions input {{
      margin-bottom: 0;
      min-width: 200px;
      flex: 1 1 220px;
    }}
    .focus-presets {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .focus-preset-chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.82);
      color: var(--ink);
      font-size: 0.84rem;
    }}
    .focus-preset-chip.active {{
      border-color: var(--accent);
      color: var(--accent);
      background: var(--accent-soft);
    }}
    .focus-preset-chip button {{
      padding: 0;
      border: 0;
      background: transparent;
      color: inherit;
      min-height: 0;
    }}
    .family-card {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      cursor: pointer;
      background: rgba(255,255,255,0.78);
      border-left: 3px solid transparent;
    }}
    .family-card.active {{
      border-color: var(--accent);
      box-shadow: inset 0 0 0 1px var(--accent);
      background: rgba(0,109,119,0.06);
    }}
    .family-card[data-status="ok"] {{ border-left-color: var(--healthy); }}
    .family-card[data-status="warning"] {{ border-left-color: var(--warning); }}
    .family-card[data-status="validation-failed"],
    .family-card[data-status="merge-failed"],
    .family-card[data-status="error"] {{ border-left-color: var(--danger); }}
    .family-card[data-status="browser-pending"] {{ border-left-color: #53616b; }}
    .family-card-head {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 6px;
    }}
    .family-card-meta {{
      display: grid;
      gap: 6px;
      font-size: 0.9rem;
    }}
    .family-card-foot {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
    }}
    .kv {{ display: grid; grid-template-columns: 180px 1fr; gap: 10px 14px; }}
    .kv dt {{ color: var(--muted); }}
    .list {{
      max-height: 220px;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 14px;
      background: rgba(255,255,255,0.6);
    }}
    .list code {{ display: block; padding: 3px 0; }}
    .empty-state {{
      border: 1px dashed var(--line);
      border-radius: 8px;
      padding: 12px 14px;
      color: var(--muted);
      background: rgba(255,255,255,0.34);
    }}
    .command-list {{
      display: grid;
      gap: 10px;
    }}
    .command-row {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 12px;
      background: rgba(255,255,255,0.6);
    }}
    .command-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 6px;
    }}
    .command-label {{
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .mini-button {{
      padding: 6px 10px;
      border-radius: 8px;
      font-size: 0.85rem;
    }}
    .tree-list {{
      max-height: 260px;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
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
    .search-row {{
      cursor: pointer;
    }}
    .search-row.active {{
      background: rgba(0,109,119,0.08);
    }}
    .symbol-link {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 4px 8px;
      background: rgba(255,255,255,0.82);
      color: var(--ink);
      cursor: pointer;
      font: inherit;
      margin: 0 6px 6px 0;
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
      border-radius: 8px;
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
    .next-step-box {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px 14px;
      background: rgba(255,255,255,0.82);
    }}
    .summary-status-line {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 10px;
    }}
    .summary-meta {{
      display: grid;
      gap: 6px;
      margin-top: 10px;
    }}
    .cards {{
      display: grid;
      gap: 10px;
      margin-top: 10px;
    }}
    .card {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px 14px;
      background: rgba(255,255,255,0.82);
    }}
    .card.healthy,
    .card.supported {{ border-color: rgba(47,107,79,0.18); background: rgba(47,107,79,0.05); }}
    .card.warning,
    .card.blocked {{ border-color: rgba(139,107,30,0.18); background: rgba(139,107,30,0.05); }}
    .card.failure,
    .card.unsupported {{ border-color: rgba(138,52,52,0.18); background: rgba(138,52,52,0.05); }}
    .card.pending {{ border-color: var(--line-strong); background: var(--neutral-soft); }}
    .card-head {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 10px;
      margin-bottom: 8px;
    }}
    .card-meta {{
      display: grid;
      gap: 6px;
      font-size: 0.92rem;
    }}
    .count-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin: 12px 0 14px;
    }}
    .count-box {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 12px;
      background: rgba(255,255,255,0.82);
    }}
    .count-box strong {{
      display: block;
      font-size: 1rem;
      margin-bottom: 3px;
    }}
    .ownership-note {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 8px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.82);
      font-size: 0.82rem;
      color: var(--muted);
    }}
    .action-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 12px 0 14px;
    }}
    .action-button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      min-height: 38px;
    }}
    .action-button.primary {{
      background: var(--accent);
      color: #ffffff;
      border-color: var(--accent);
    }}
    .action-button.secondary {{
      background: rgba(255,255,255,0.82);
      color: var(--ink);
    }}
    .command-drawer {{
      margin-top: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.72);
    }}
    .command-drawer summary {{
      list-style: none;
      cursor: pointer;
      padding: 12px 14px;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .command-drawer summary::-webkit-details-marker {{
      display: none;
    }}
    .command-drawer-body {{
      padding: 0 12px 12px;
    }}
    @media (max-width: 1320px) {{
      .grid {{
        grid-template-columns: 280px minmax(0, 1fr);
      }}
      .grid > section.panel:last-child {{
        grid-column: 1 / -1;
      }}
      .summary-grid {{
        grid-template-columns: 1fr;
      }}
    }}
    @media (max-width: 1100px) {{
      .hero, .grid, .split, .builder-grid, .summary-grid, .summary-stats, .count-grid {{ grid-template-columns: 1fr; }}
      .family-list {{ max-height: none; }}
      .workspace-tabs {{ overflow-x: auto; flex-wrap: nowrap; padding-bottom: 4px; }}
      .focus-advanced-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <section class="panel">
        <div class="surface-kicker">HLA Studio Surface</div>
        <h1>FOM Explorer</h1>
        <p class="muted"><strong>Alias:</strong> FOM Workbench snapshot and tool routes remain valid.</p>
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
        <select id="status-filter">
          <option value="">all statuses</option>
          <option value="ok">ok</option>
          <option value="warning">warning</option>
          <option value="merge-failed">merge failed</option>
          <option value="validation-failed">validation failed</option>
          <option value="browser-pending">browser pending</option>
          <option value="error">error</option>
        </select>
        <select id="edition-filter">
          <option value="">all edition scopes</option>
          <option value="2010 only">2010 only</option>
          <option value="2025 only">2025 only</option>
          <option value="cross-edition / ambiguous">cross-edition / ambiguous</option>
          <option value="both">both</option>
        </select>
        <select id="baseline-filter">
          <option value="">all baselines</option>
          <option value="repo-owned">repo-owned</option>
          <option value="third-party">third-party</option>
          <option value="external">external</option>
        </select>
        <select id="load-mode-filter">
          <option value="">all load modes</option>
          <option value="standalone">standalone</option>
          <option value="base-plus-extension">base-plus-extension</option>
          <option value="ordered-family">ordered-family</option>
          <option value="browser-saved">browser-saved</option>
          <option value="custom">custom</option>
        </select>
        <div id="family-list" class="family-list" tabindex="0"></div>
        <div class="rail-section">
          <div class="section-title">
            <h3 style="margin: 0;">Recent Selections</h3>
            <span class="muted">session memory</span>
          </div>
          <div id="recent-selections" class="history-list"></div>
        </div>
        <div class="edit-box" style="margin-top: 14px;">
          <h3>Custom Load Set Builder</h3>
          <input id="builder-name" type="text" placeholder="saved load set name">
          <input id="builder-filter" type="search" placeholder="Filter baseline entries by id, family, edition, or path">
          <div id="builder-health" class="list" style="margin-bottom: 10px;"></div>
          <div id="builder-selected" class="list" style="margin-bottom: 10px;"></div>
          <div id="builder-entry-list" class="list checkbox-list"></div>
          <div class="builder-grid">
            <button id="builder-save" type="button">save set</button>
            <button id="builder-clear" type="button">clear selection</button>
          </div>
          <div class="builder-grid">
            <button id="builder-export" type="button">export sets</button>
            <button id="builder-import" type="button">import sets</button>
          </div>
          <textarea id="builder-transfer" placeholder="paste exported custom load set JSON here"></textarea>
          <div id="builder-saved" class="list" style="margin-top: 10px;"></div>
          <div id="builder-command" class="list" style="margin-top: 10px;"></div>
        </div>
      </section>
      <div class="workspace-stack">
        <section class="panel summary-panel">
          <div id="selection-summary" class="summary-grid">
            <div class="empty-state">Select a family or custom load set to begin.</div>
          </div>
        </section>
        <section class="panel">
          <div class="section-title">
            <h2 style="margin: 0;">Workspace</h2>
            <span class="muted">one active task at a time</span>
          </div>
          <div class="workspace-tabs" id="workspace-tabs">
            <button class="workspace-tab active" type="button" data-workspace="overview">Overview</button>
            <button class="workspace-tab" type="button" data-workspace="conflict">Conflict</button>
            <button class="workspace-tab" type="button" data-workspace="validation">Validation</button>
            <button class="workspace-tab" type="button" data-workspace="diff">Diff</button>
            <button class="workspace-tab" type="button" data-workspace="repair">Repair</button>
          </div>
          <div class="focus-bar" id="workspace-focus-controls">
            <div class="focus-chips">
              <button class="focus-chip active" type="button" data-focus-kind="all">All</button>
              <button class="focus-chip" type="button" data-focus-kind="object">Objects</button>
              <button class="focus-chip" type="button" data-focus-kind="interaction">Interactions</button>
              <button class="focus-chip" type="button" data-focus-kind="datatype">Datatypes</button>
              <button class="focus-chip" type="button" data-focus-kind="dimension">Dimensions</button>
              <button class="focus-chip" type="button" data-focus-kind="issues">Issues</button>
              <button class="focus-chip" type="button" data-focus-kind="changed">Changed</button>
            </div>
            <input id="workspace-focus-filter" class="focus-input" type="search" placeholder="Focus symbol or selector: Track kind:object owner:repo-owned changed:true">
            <div id="workspace-focus-status" class="focus-status">Focus: all workspace rows</div>
            <details class="focus-advanced" id="workspace-focus-advanced">
              <summary>Advanced focus</summary>
              <div class="focus-advanced-body">
                <div class="focus-advanced-grid">
                  <select id="focus-kind-select">
                    <option value="all">all kinds</option>
                    <option value="object">objects</option>
                    <option value="interaction">interactions</option>
                    <option value="datatype">datatypes</option>
                    <option value="dimension">dimensions</option>
                  </select>
                  <select id="focus-owner-select">
                    <option value="">all owners</option>
                    <option value="repo-owned">repo-owned</option>
                    <option value="third-party">third-party</option>
                    <option value="external">external</option>
                  </select>
                  <select id="focus-issues-select">
                    <option value="">all issue states</option>
                    <option value="true">issues only</option>
                  </select>
                  <select id="focus-changed-select">
                    <option value="">all change states</option>
                    <option value="true">changed only</option>
                  </select>
                  <input id="focus-symbol-input" type="search" placeholder="symbol">
                  <input id="focus-terms-input" type="search" placeholder="plain terms">
                </div>
                <div class="focus-actions">
                  <button id="focus-apply" type="button">apply focus</button>
                  <button id="focus-clear" type="button">clear focus</button>
                  <input id="focus-preset-name" type="text" placeholder="saved view name">
                  <button id="focus-save-preset" type="button">save view</button>
                </div>
                <div id="focus-presets" class="focus-presets"></div>
              </div>
            </details>
          </div>
          <div id="workspace-overview" class="workspace-pane active">
            <div class="section-title">
              <h3 style="margin: 0;">Overview</h3>
              <span class="muted">selection, merged shape, and validation entry points</span>
            </div>
            <div id="inspect-panel" class="muted">Select a family or custom load set.</div>
          </div>
          <div id="workspace-conflict" class="workspace-pane">
            <div class="section-title">
              <h3 style="margin: 0;">Conflict</h3>
              <span class="muted">why merge failed and who owns the declaration</span>
            </div>
            <div id="conflict-panel" class="muted">Select a family or custom load set to inspect conflict state.</div>
          </div>
          <div id="workspace-validation" class="workspace-pane">
            <div class="section-title">
              <h3 style="margin: 0;">Validation</h3>
              <span class="muted">issue groups, severity, and report entry points</span>
            </div>
            <div id="validation-panel" class="muted">Select a family or custom load set to inspect validation state.</div>
          </div>
          <div id="workspace-diff" class="workspace-pane">
            <div class="section-title">
              <h3 style="margin: 0;">Diff</h3>
              <span class="muted">compare the active selection against another family or load set</span>
            </div>
            <div class="split">
              <select id="left-family"></select>
              <select id="right-family"></select>
            </div>
            <div class="toolbar" style="margin-top: 10px;">
              <input id="custom-left" type="text" placeholder="custom left set: id1,id2">
              <input id="custom-right" type="text" placeholder="custom right set: id1,id2">
            </div>
            <div id="recent-comparisons" class="history-list" style="margin: 0 0 14px;"></div>
            <div id="diff-panel" class="muted" style="margin-top: 14px;">Select two families to compare.</div>
          </div>
          <div id="workspace-repair" class="workspace-pane">
            <div class="section-title">
              <h3 style="margin: 0;">Repair</h3>
              <span class="muted">repo-owned fixes, guarded edits, and regeneration steps</span>
            </div>
            <div class="edit-box">
              <div id="edit-summary" class="muted"></div>
              <textarea id="edit-description" placeholder="Proposed description"></textarea>
              <input id="edit-keywords" type="text" placeholder="Keywords to append, comma-separated">
              <input id="edit-notes" type="text" placeholder="Notes to append, comma-separated">
              <div id="edit-command" class="list"></div>
            </div>
          </div>
        </section>
      </div>
      <section class="panel">
        <div class="rail-section">
          <div class="section-title">
            <h2 style="margin: 0;">Investigation</h2>
            <span id="active-symbol-summary" class="muted">No symbol pinned.</span>
          </div>
          <div class="toolbar">
            <select id="tree-kind">
              <option value="object">object classes</option>
              <option value="interaction">interaction classes</option>
            </select>
            <input id="tree-filter" type="search" placeholder="Filter hierarchy">
          </div>
          <div id="tree-panel" class="tree-list"></div>
          <div id="node-panel" class="panel" style="padding: 14px; margin-top: 12px;"></div>
        </div>
        <div class="rail-section">
          <div class="section-title">
            <h3 style="margin: 0;">Search</h3>
            <span class="muted">merged names in current scope</span>
          </div>
          <input id="search-filter" type="search" placeholder="Search object, interaction, or datatype names">
          <table>
            <thead><tr><th>Kind</th><th>Name</th><th>Family</th></tr></thead>
            <tbody id="search-results"></tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
  <script>
    const snapshot = {payload};
    const browserStorageKey = "hla2010-fom-workbench-custom-load-sets";
    const focusPresetStorageKey = "hla2010-fom-workbench-focus-presets";
    const familyMap = new Map(snapshot.families.map((family) => [family.scenario_family, family]));
    const diffMap = new Map(snapshot.diffs.map((diff) => [`${{diff.left_family}}::${{diff.right_family}}`, diff]));
    const entryMap = new Map(snapshot.entries.map((entry) => [entry.id, entry]));
    const fixedCustomLoadSetNames = new Set(snapshot.custom_load_sets.map((loadSet) => loadSet.name));
    const fixedFamilyNames = new Set(snapshot.families.map((family) => family.scenario_family));
    let browserCustomLoadSets = loadBrowserCustomLoadSets();
    let builderSelectedMemberIds = [];
    let selectedCatalogKind = snapshot.families[0] ? "family" : "custom-load-set";
    let selectedCatalogName = snapshot.families[0]?.scenario_family || customLoadSets()[0]?.name || null;
    let selectedNodeName = null;
    let selectedSearchName = null;
    let currentWorkspaceMode = "overview";
    let focusKind = "all";
    let focusSelector = "";
    let focusPresets = loadFocusPresets();
    let recentSelections = [];
    let recentComparisons = [];

    function setCapabilities() {{
      const host = document.getElementById("capabilities");
      host.innerHTML = Object.entries(snapshot.capabilities)
        .map(([key, value]) => `<span class="pill">${{key}}: ${{String(value)}}</span>`)
        .join("");
    }}

    function escapeHtml(value) {{
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }}

    function emptyState(message) {{
      return `<div class="empty-state">${{escapeHtml(message)}}</div>`;
    }}

    function sourceLabel(item) {{
      if (!item) return "selection";
      if (item.source_kind === "browser-saved-custom-load-set") return "browser-saved load set";
      if (item.source_kind === "snapshot-custom-load-set") return "generated load set";
      if (item.name) return "custom load set";
      return "family";
    }}

    function ownershipLabel(item) {{
      const baselines = item?.baseline_kinds || [];
      if (!baselines.length) return "custom";
      if (baselines.length === 1) return baselines[0];
      return baselines.join(" + ");
    }}

    function severityClass(status, verdict = null) {{
      if (status === "ok" && verdict === "conforming") return "healthy";
      if (status === "ok") return "healthy";
      if (status === "warning" || status === "blocked") return "warning";
      if (status === "browser-pending") return "pending";
      if (status === "merge-failed" || status === "validation-failed" || status === "error" || status === "unsupported") return "failure";
      if (status === "supported") return "healthy";
      return "pending";
    }}

    function issueSummaryLabel(item) {{
      if (!item) return "No selection";
      if (catalogStatus(item) === "browser-pending") return "Snapshot refresh required";
      if (item.validation_issue_count) return `${{item.validation_issue_count}} issue${{item.validation_issue_count === 1 ? "" : "s"}}`;
      if (item.merge_conflict_symbol) return `Conflict: ${{item.merge_conflict_symbol}}`;
      return "No active issue";
    }}

    function displayText(value, fallback = "not available") {{
      if (Array.isArray(value)) return value.length ? value.join(", ") : fallback;
      if (value === null || value === undefined || value === "") return fallback;
      return String(value);
    }}

    function parsedFocusSelector() {{
      const parsed = {{
        terms: [],
        kind: null,
        owner: null,
        symbol: null,
        changed: null,
        issue: null,
      }};
      for (const token of focusSelector.trim().split(/\\s+/).filter(Boolean)) {{
        const parts = token.split(":");
        const key = parts[0].toLowerCase();
        const value = parts.slice(1).join(":").toLowerCase();
        if (parts.length > 1 && ["kind", "owner", "symbol", "name", "changed", "issue"].includes(key)) {{
          if (key === "kind") parsed.kind = value;
          else if (key === "owner") parsed.owner = value;
          else if (key === "symbol" || key === "name") parsed.symbol = value;
          else if (key === "changed") parsed.changed = value !== "false" && value !== "0";
          else if (key === "issue") parsed.issue = value !== "false" && value !== "0";
        }} else {{
          parsed.terms.push(token.toLowerCase());
        }}
      }}
      if (focusKind === "object" || focusKind === "interaction" || focusKind === "datatype" || focusKind === "dimension") {{
        parsed.kind = focusKind;
      }} else if (focusKind === "issues") {{
        parsed.issue = true;
      }} else if (focusKind === "changed") {{
        parsed.changed = true;
      }}
      return parsed;
    }}

    function serializeFocusSelector(parts) {{
      const tokens = [];
      if (parts.owner) tokens.push(`owner:${{parts.owner}}`);
      if (parts.symbol) tokens.push(`symbol:${{parts.symbol}}`);
      if (parts.issue) tokens.push("issue:true");
      if (parts.changed) tokens.push("changed:true");
      if (parts.terms) {{
        for (const term of parts.terms.split(/\\s+/).filter(Boolean)) tokens.push(term);
      }}
      return tokens.join(" ").trim();
    }}

    function focusIsActive() {{
      return focusKind !== "all" || Boolean(focusSelector.trim());
    }}

    function focusSummary() {{
      const parts = [];
      if (focusKind !== "all") parts.push(focusKind);
      if (focusSelector.trim()) parts.push(focusSelector.trim());
      return parts.length ? `Focus: ${{parts.join(" + ")}}` : "Focus: all workspace rows";
    }}

    function matchesFocus(kind, values, options = {{}}) {{
      const parsed = parsedFocusSelector();
      const haystack = values
        .flatMap((value) => Array.isArray(value) ? value : [value])
        .filter((value) => value !== null && value !== undefined)
        .join(" ")
        .toLowerCase();
      if (parsed.kind && !options.ignoreKind && kind !== parsed.kind) return false;
      if (parsed.owner) {{
        const owners = (options.owners || []).join(" ").toLowerCase();
        if (!owners.includes(parsed.owner)) return false;
      }}
      if (parsed.symbol && !haystack.includes(parsed.symbol)) return false;
      if (parsed.issue && options.issue === false) return false;
      if (parsed.changed && options.changed === false) return false;
      return parsed.terms.every((term) => haystack.includes(term));
    }}

    function loadFocusPresets() {{
      try {{
        const raw = window.localStorage.getItem(focusPresetStorageKey);
        if (!raw) return [];
        const parsed = JSON.parse(raw);
        if (!Array.isArray(parsed)) return [];
        return parsed.filter((row) => row && typeof row.name === "string" && typeof row.kind === "string" && typeof row.selector === "string");
      }} catch (_error) {{
        return [];
      }}
    }}

    function saveFocusPresets() {{
      window.localStorage.setItem(focusPresetStorageKey, JSON.stringify(focusPresets));
    }}

    function populateAdvancedFocusForm() {{
      const parsed = parsedFocusSelector();
      document.getElementById("focus-kind-select").value = focusKind;
      document.getElementById("focus-owner-select").value = parsed.owner || "";
      document.getElementById("focus-issues-select").value = parsed.issue ? "true" : "";
      document.getElementById("focus-changed-select").value = parsed.changed ? "true" : "";
      document.getElementById("focus-symbol-input").value = parsed.symbol || "";
      document.getElementById("focus-terms-input").value = (parsed.terms || []).join(" ");
    }}

    function renderFocusPresets() {{
      const host = document.getElementById("focus-presets");
      if (!host) return;
      if (!focusPresets.length) {{
        host.innerHTML = emptyState("Saved focus views appear here.");
        return;
      }}
      host.innerHTML = focusPresets.map((preset) => `
        <div class="focus-preset-chip${{preset.kind === focusKind && preset.selector === focusSelector ? " active" : ""}}">
          <button type="button" data-focus-preset="${{preset.name}}">${{preset.name}}</button>
          <button type="button" data-delete-focus-preset="${{preset.name}}" aria-label="delete saved focus">x</button>
        </div>
      `).join("");
      host.querySelectorAll("button[data-focus-preset]").forEach((button) => {{
        button.onclick = () => {{
          const preset = focusPresets.find((row) => row.name === button.dataset.focusPreset);
          if (!preset) return;
          focusKind = preset.kind;
          focusSelector = preset.selector;
          populateAdvancedFocusForm();
          rerenderFocusedViews();
        }};
      }});
      host.querySelectorAll("button[data-delete-focus-preset]").forEach((button) => {{
        button.onclick = () => {{
          focusPresets = focusPresets.filter((row) => row.name !== button.dataset.deleteFocusPreset);
          saveFocusPresets();
          renderFocusPresets();
        }};
      }});
    }}

    function applyAdvancedFocusForm() {{
      focusKind = document.getElementById("focus-kind-select").value || "all";
      focusSelector = serializeFocusSelector({{
        owner: document.getElementById("focus-owner-select").value.trim(),
        symbol: document.getElementById("focus-symbol-input").value.trim(),
        issue: document.getElementById("focus-issues-select").value === "true",
        changed: document.getElementById("focus-changed-select").value === "true",
        terms: document.getElementById("focus-terms-input").value.trim(),
      }});
      rerenderFocusedViews();
    }}

    function clearFocus() {{
      focusKind = "all";
      focusSelector = "";
      populateAdvancedFocusForm();
      rerenderFocusedViews();
    }}

    function saveCurrentFocusPreset() {{
      const name = document.getElementById("focus-preset-name").value.trim();
      if (!name) {{
        renderFocusPresets();
        return;
      }}
      focusPresets = focusPresets.filter((row) => row.name !== name);
      focusPresets.push({{ name, kind: focusKind, selector: focusSelector }});
      focusPresets.sort((left, right) => left.name.localeCompare(right.name));
      saveFocusPresets();
      renderFocusPresets();
    }}

    function renderFocusControls() {{
      document.querySelectorAll(".focus-chip").forEach((button) => {{
        button.classList.toggle("active", button.dataset.focusKind === focusKind);
      }});
      const input = document.getElementById("workspace-focus-filter");
      if (input && input.value !== focusSelector) input.value = focusSelector;
      const status = document.getElementById("workspace-focus-status");
      if (status) status.textContent = focusSummary();
      populateAdvancedFocusForm();
      renderFocusPresets();
    }}

    function rerenderFocusedViews() {{
      renderFocusControls();
      renderSelectionSummary();
      renderSearch();
      renderTree();
      renderValidationWorkspace();
      renderDiff();
    }}

    function selectionKey(kind, name) {{
      return `${{kind}}::${{name}}`;
    }}

    function rememberSelection(kind, name) {{
      if (!name) return;
      const item = currentCatalogItem();
      const entry = {{
        kind,
        name,
        source: item ? sourceLabel(item) : kind,
        status: item ? catalogStatus(item) : "unknown",
      }};
      recentSelections = [entry, ...recentSelections.filter((row) => selectionKey(row.kind, row.name) !== selectionKey(kind, name))].slice(0, 6);
    }}

    function renderRecentSelections() {{
      const host = document.getElementById("recent-selections");
      if (!host) return;
      if (!recentSelections.length) {{
        host.innerHTML = emptyState("Recent selections appear here during this session.");
        return;
      }}
      host.innerHTML = recentSelections.map((entry) => `
        <button class="history-chip${{entry.kind === selectedCatalogKind && entry.name === selectedCatalogName ? " active" : ""}}" type="button" data-recent-kind="${{entry.kind}}" data-recent-name="${{entry.name}}">
          <span>${{entry.name}}</span>
          <span class="muted">${{entry.source}}</span>
        </button>
      `).join("");
      host.querySelectorAll("button[data-recent-kind]").forEach((button) => {{
        button.onclick = () => {{
          document.getElementById("catalog-mode").value = button.dataset.recentKind;
          selectedCatalogKind = button.dataset.recentKind;
          selectedCatalogName = button.dataset.recentName;
          selectedNodeName = null;
          selectedSearchName = null;
          setDiffSelectors();
          refreshSelectionViews({{ preserveMode: true }});
        }};
      }});
    }}

    function rememberComparison(left, right) {{
      if (!left || !right || left === right) return;
      const key = `${{left}}::${{right}}`;
      recentComparisons = [{{ left, right, key }}, ...recentComparisons.filter((row) => row.key !== key)].slice(0, 6);
    }}

    function renderRecentComparisons() {{
      const host = document.getElementById("recent-comparisons");
      if (!host) return;
      if (!recentComparisons.length) {{
        host.innerHTML = emptyState("Recent comparisons appear after you compare two selections.");
        return;
      }}
      const activeLeft = document.getElementById("left-family")?.value || "";
      const activeRight = document.getElementById("right-family")?.value || "";
      host.innerHTML = recentComparisons.map((entry) => `
        <button class="history-chip${{entry.left === activeLeft && entry.right === activeRight ? " active" : ""}}" type="button" data-left="${{entry.left}}" data-right="${{entry.right}}">
          <span>${{entry.left}}</span>
          <span class="muted">vs</span>
          <span>${{entry.right}}</span>
        </button>
      `).join("");
      host.querySelectorAll("button[data-left]").forEach((button) => {{
        button.onclick = () => {{
          currentWorkspaceMode = "diff";
          renderWorkspaceMode();
          document.getElementById("left-family").value = button.dataset.left;
          document.getElementById("right-family").value = button.dataset.right;
          renderSelectionSummary();
          renderDiff();
        }};
      }});
    }}

    function preferredWorkspaceMode(item) {{
      if (!item) return "overview";
      const status = catalogStatus(item);
      if (status === "merge-failed" || item.parse_error_kind === "merge") return "conflict";
      if (status === "validation-failed" || status === "warning") return "validation";
      if ((item.merge_conflict_member_details || []).length) return "repair";
      return "overview";
    }}

    function activeSymbolLabel() {{
      return selectedNodeName || selectedSearchName || null;
    }}

    function hashParams() {{
      const raw = window.location.hash.startsWith("#") ? window.location.hash.slice(1) : "";
      return new URLSearchParams(raw);
    }}

    function updateDeepLinkHash() {{
      const params = new URLSearchParams();
      if (selectedCatalogKind === "custom-load-set" && selectedCatalogName) {{
        params.set("load-set", selectedCatalogName);
      }} else if (selectedCatalogName) {{
        params.set("family", selectedCatalogName);
      }}
      if (currentWorkspaceMode && currentWorkspaceMode !== "overview") {{
        params.set("workspace", currentWorkspaceMode);
      }}
      const symbol = activeSymbolLabel();
      if (symbol) {{
        params.set("symbol", symbol);
      }}
      const hash = params.toString();
      history.replaceState(null, "", hash ? `#${{hash}}` : window.location.pathname + window.location.search);
    }}

    function applyInitialDeepLink() {{
      const params = hashParams();
      const family = params.get("family");
      const loadSet = params.get("load-set");
      const workspace = params.get("workspace");
      const symbol = params.get("symbol");
      const symbolKind = params.get("kind");
      if (family && familyMap.has(family)) {{
        selectedCatalogKind = "family";
        selectedCatalogName = family;
      }} else if (loadSet && customLoadSets().some((row) => row.name === loadSet)) {{
        selectedCatalogKind = "custom-load-set";
        selectedCatalogName = loadSet;
      }}
      if (workspace) {{
        currentWorkspaceMode = workspace;
      }}
      if (symbol) {{
        selectedNodeName = symbol;
        selectedSearchName = symbol;
      }}
      if (symbolKind && (symbolKind === "object" || symbolKind === "interaction")) {{
        document.getElementById("tree-kind").value = symbolKind;
      }}
    }}

    function renderWorkspaceMode() {{
      document.querySelectorAll(".workspace-tab").forEach((button) => {{
        button.classList.toggle("active", button.dataset.workspace === currentWorkspaceMode);
      }});
      document.querySelectorAll(".workspace-pane").forEach((pane) => {{
        pane.classList.toggle("active", pane.id === `workspace-${{currentWorkspaceMode}}`);
      }});
      const symbolSummary = document.getElementById("active-symbol-summary");
      if (symbolSummary) {{
        const symbol = activeSymbolLabel();
        symbolSummary.textContent = symbol ? `Pinned symbol: ${{symbol}}` : "No symbol pinned.";
      }}
    }}

    function renderSelectionSummary() {{
      const host = document.getElementById("selection-summary");
      const item = currentCatalogItem();
      if (!item) {{
        host.innerHTML = emptyState("Select a family or custom load set to begin.");
        return;
      }}
      const status = catalogStatus(item);
      const severity = severityClass(status, item.validation_verdict);
      const nextAction = currentWorkspaceMode === "conflict"
        ? "Inspect the conflicting declaration and move toward repair."
        : currentWorkspaceMode === "validation"
          ? "Review issue groups and jump into the affected symbol."
          : currentWorkspaceMode === "diff"
            ? "Compare this selection against a peer and inspect the deltas."
            : currentWorkspaceMode === "repair"
              ? "Stage a repo-owned fix or copy the guarded command bundle."
              : item.recommended_next_step || "Inspect the merged shape and validation entry points.";
      host.innerHTML = `
        <div>
          <div class="surface-kicker">${{sourceLabel(item)}}</div>
          <div class="summary-title">
            <h2 style="margin: 0;">${{selectionLabel(item)}}</h2>
          </div>
          <div class="summary-status-line">
            ${{statusPill(status)}}
            ${{item.validation_verdict ? statusPill(item.validation_verdict.replaceAll(" ", "-")) : ""}}
            <span class="ownership-note">ownership: ${{ownershipLabel(item)}}</span>
          </div>
          <div class="next-step-box">
            <div class="stat-label">Next action</div>
            <div>${{nextAction}}</div>
          </div>
          <div class="summary-meta">
            <div class="muted">${{(item.edition_classes || ["custom"]).join(", ")}} | ${{displayText(item.edition_scope)}} | ${{item.load_mode}}</div>
            <div class="muted">Members: ${{displayText(item.member_ids, "none")}}</div>
          </div>
        </div>
        <div class="summary-stats">
          <div class="stat-box">
            <div class="stat-label">Merged shape</div>
            <div>${{item.object_class_count}} objects</div>
            <div>${{item.interaction_class_count}} interactions</div>
            <div>${{item.datatype_count}} datatypes</div>
          </div>
          <div class="stat-box ${{severity}}">
            <div class="stat-label">Current state</div>
            <div>${{issueSummaryLabel(item)}}</div>
            <div>Validation: ${{displayText(item.validation_verdict)}}</div>
            <div>Conflict: ${{displayText(item.merge_conflict_symbol, "none")}}</div>
          </div>
        </div>
      `;
    }}

    function refreshSelectionViews(options = {{}}) {{
      const preserveMode = options.preserveMode === true;
      if (!preserveMode) {{
        currentWorkspaceMode = preferredWorkspaceMode(currentCatalogItem());
      }}
      rememberSelection(selectedCatalogKind, selectedCatalogName);
      renderFocusControls();
      renderWorkspaceMode();
      renderSelectionSummary();
      renderFamilyList();
      renderRecentSelections();
      renderInspect();
      renderConflictWorkspace();
      renderValidationWorkspace();
      renderSearch();
      syncDiffSelectionToCatalog();
      renderDiff();
      updateDeepLinkHash();
    }}

    function renderCommandList(items, emptyMessage = "No command available.") {{
      if (!items || !items.length) return emptyState(emptyMessage);
      return `<div class="command-list">${{items.map((item, index) => `
        <div class="command-row">
          <div class="command-head">
            <span class="command-label">${{escapeHtml(item.label || `command ${{index + 1}}`)}}</span>
            <button class="mini-button" type="button" data-copy-text="${{escapeHtml(item.command || "")}}">${{item.copyLabel || "copy"}}</button>
          </div>
          <code>${{escapeHtml(item.command || "")}}</code>
        </div>
      `).join("")}}</div>`;
    }}

    function renderActionBar(actions) {{
      const valid = (actions || []).filter((action) => action && action.label);
      if (!valid.length) return "";
      return `<div class="action-bar">${{valid.map((action) => {{
        const kind = action.kind || "secondary";
        const disabled = action.disabled ? "disabled" : "";
        const attrs = [
          action.command ? `data-copy-text="${{escapeHtml(action.command)}}"` : "",
          action.href ? `data-open-href="${{escapeHtml(action.href)}}"` : "",
          action.workspace ? `data-workspace-target="${{escapeHtml(action.workspace)}}"` : "",
          action.symbol ? `data-jump-symbol="${{escapeHtml(action.symbol)}}"` : "",
          action.symbolKind ? `data-jump-kind="${{escapeHtml(action.symbolKind)}}"` : "",
        ].filter(Boolean).join(" ");
        return `<button class="action-button ${{kind}}" type="button" ${{attrs}} ${{disabled}}>${{escapeHtml(action.label)}}</button>`;
      }}).join("")}}</div>`;
    }}

    function renderCommandDrawer(title, commands, emptyMessage = "No command available.") {{
      if (!commands || !commands.length) return "";
      return `
        <details class="command-drawer">
          <summary>${{escapeHtml(title)}}</summary>
          <div class="command-drawer-body">
            ${{renderCommandList(commands, emptyMessage)}}
          </div>
        </details>
      `;
    }}

    function wireCopyButtons(host = document) {{
      host.querySelectorAll("button[data-copy-text]").forEach((element) => {{
        element.onclick = async () => {{
          const value = element.dataset.copyText || "";
          try {{
            if (navigator.clipboard && navigator.clipboard.writeText) {{
              await navigator.clipboard.writeText(value);
            }}
          }} catch (_error) {{
          }}
          const prior = element.textContent;
          element.textContent = "copied";
          window.setTimeout(() => {{
            element.textContent = prior;
          }}, 1200);
        }};
      }});
    }}

    function wireActionButtons(host = document) {{
      host.querySelectorAll("button[data-open-href]").forEach((element) => {{
        element.onclick = () => {{
          const href = element.dataset.openHref;
          if (!href) return;
          window.open(href, "_blank", "noopener");
        }};
      }});
      host.querySelectorAll("button[data-workspace-target]").forEach((element) => {{
        element.onclick = () => {{
          currentWorkspaceMode = element.dataset.workspaceTarget;
          renderWorkspaceMode();
          renderSelectionSummary();
        }};
      }});
      host.querySelectorAll("button[data-jump-symbol]").forEach((element) => {{
        element.onclick = () => {{
          jumpToSymbol(element.dataset.jumpSymbol, {{
            kind: element.dataset.jumpKind || null,
            setFilter: true,
          }});
        }};
      }});
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
        const memberIds = [...new Set(row.member_ids.filter((id) => entryMap.has(id)))];
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

    function builderHas(id) {{
      return builderSelectedMemberIds.includes(id);
    }}

    function builderAdd(id) {{
      if (!builderHas(id)) builderSelectedMemberIds.push(id);
    }}

    function builderRemove(id) {{
      builderSelectedMemberIds = builderSelectedMemberIds.filter((value) => value !== id);
    }}

    function builderMove(id, delta) {{
      const index = builderSelectedMemberIds.indexOf(id);
      if (index < 0) return;
      const next = index + delta;
      if (next < 0 || next >= builderSelectedMemberIds.length) return;
      const copy = [...builderSelectedMemberIds];
      [copy[index], copy[next]] = [copy[next], copy[index]];
      builderSelectedMemberIds = copy;
    }}

    function hydratedBrowserLoadSet(row) {{
      const members = row.member_ids.map((id) => entryMap.get(id)).filter(Boolean);
      const editionClasses = [...new Set(members.map((entry) => entry.edition_class))].sort();
      const editionScopes = [...new Set(members.map((entry) => entry.edition_scope))].sort();
      const baselineKinds = [...new Set(members.map((entry) => entry.baseline_kind))].sort();
      return {{
        name: row.name,
        member_ids: [...row.member_ids],
        member_paths: members.map((entry) => entry.path),
        parse_status: "browser-pending",
        parse_error_kind: "snapshot-required",
        parse_error: "Regenerate the workbench snapshot with the command below to compute parsed trees, diffs, and validation packets.",
        recommended_next_step: "Regenerate the workbench snapshot with this custom load set to compute parsed trees, diffs, and validation packets.",
        merge_conflict_kind: null,
        merge_conflict_symbol: null,
        merge_conflict_members: [],
        merge_conflict_member_details: [],
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
        catalog_status: "browser-pending",
        validation_verdict: null,
        validation_passed: null,
        validation_issue_count: 0,
        validation_issue_layers: [],
        validation_issue_groups: [],
        datatype_normalizations: [],
        edition_classes: editionClasses,
        edition_scope: editionScopes.length === 1 ? editionScopes[0] : "cross-edition / ambiguous",
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

    function evaluateBuilderSelection(memberIds) {{
      const members = memberIds.map((id) => entryMap.get(id)).filter(Boolean);
      if (!members.length) {{
        return {{
          label: "unknown",
          warnings: ["Select one or more baseline entries to evaluate a candidate load set."],
          editionScope: "n/a",
          baselineKinds: [],
          loadModes: [],
        }};
      }}
      const editionScopes = [...new Set(members.map((entry) => entry.edition_scope))];
      const baselineKinds = [...new Set(members.map((entry) => entry.baseline_kind))];
      const loadModes = [...new Set(members.map((entry) => entry.load_mode))];
      const warnings = [];
      let label = "likely clean";

      const selectedSet = new Set(memberIds);
      const hasProtoExtension = members.some((entry) => entry.load_mode === "base-plus-extension" && entry.id !== "repo-2025-proto-base");
      if (hasProtoExtension && !selectedSet.has("repo-2025-proto-base")) {{
        label = "known conflict";
        warnings.push("One or more base-plus-extension members are selected without repo-2025-proto-base.");
      }}

      const editionClasses = [...new Set(members.map((entry) => entry.edition_class))];
      if (editionClasses.length > 1 || editionScopes.length > 1) {{
        if (label !== "known conflict") label = "known warning";
        warnings.push("The candidate mixes multiple edition classes or edition scopes.");
      }}

      const scenarioFamilies = [...new Set(members.map((entry) => entry.scenario_family))];
      if (scenarioFamilies.length > 1 && label === "likely clean") {{
        label = "known warning";
        warnings.push("The candidate spans multiple scenario families and should be regenerated before relying on merged behavior.");
      }}

      const orderedFamilyMembers = members.filter((entry) => entry.load_mode === "ordered-family");
      if (orderedFamilyMembers.length > 1) {{
        const orderedFamilies = [...new Set(orderedFamilyMembers.map((entry) => entry.scenario_family))];
        if (orderedFamilies.length > 1) {{
          if (label !== "known conflict") label = "known warning";
          warnings.push("Ordered-family members from different families are selected together.");
        }}
      }}

      return {{
        label,
        warnings: warnings.length ? warnings : ["No obvious repo-known merge hazard detected from the current selection."],
        editionScope: editionScopes.length === 1 ? editionScopes[0] : "cross-edition / ambiguous",
        baselineKinds,
        loadModes,
      }};
    }}

    function currentCatalogItems() {{
      return selectedCatalogKind === "custom-load-set" ? customLoadSets() : snapshot.families;
    }}

    function currentCatalogItem() {{
      if (selectedCatalogKind === "custom-load-set") return customLoadSets().find((loadSet) => loadSet.name === selectedCatalogName) || null;
      return familyMap.get(selectedCatalogName) || null;
    }}

    function catalogStatus(item) {{
      return item.catalog_status || (item.parse_status === "browser-pending" ? "browser-pending" : item.parse_status === "ok" ? "ok" : "error");
    }}

    function statusPill(status) {{
      return `<span class="pill status-${{status}}">${{status.replaceAll("-", " ")}}</span>`;
    }}

    function catalogSearchText(family) {{
      return [
        family.scenario_family || family.name,
        (family.edition_classes || []).join(" "),
        family.edition_scope || "",
        (family.baseline_kinds || []).join(" "),
        family.load_mode,
        family.member_ids.join(" "),
      ].join(" ").toLowerCase();
    }}

    function renderFamilyList() {{
      const filter = document.getElementById("family-filter").value.trim().toLowerCase();
      const statusFilter = document.getElementById("status-filter").value;
      const editionFilter = document.getElementById("edition-filter").value;
      const baselineFilter = document.getElementById("baseline-filter").value;
      const loadModeFilter = document.getElementById("load-mode-filter").value;
      const host = document.getElementById("family-list");
      host.innerHTML = "";
      for (const family of currentCatalogItems()) {{
        const catalogName = family.scenario_family || family.name;
        if (filter && !catalogSearchText(family).includes(filter)) continue;
        if (statusFilter && catalogStatus(family) !== statusFilter) continue;
        if (editionFilter && (family.edition_scope || "") !== editionFilter) continue;
        if (baselineFilter && !(family.baseline_kinds || []).includes(baselineFilter)) continue;
        if (loadModeFilter && (family.load_mode || "") !== loadModeFilter) continue;
        const card = document.createElement("div");
        card.className = "family-card" + (catalogName === selectedCatalogName ? " active" : "");
        card.dataset.status = catalogStatus(family);
        card.innerHTML = `
          <div class="family-card-head">
            <strong>${{catalogName}}</strong>
            ${{statusPill(catalogStatus(family))}}
          </div>
          <div class="family-card-meta">
            <div class="muted">${{sourceLabel(family)}} | ${{ownershipLabel(family)}}</div>
            <div class="muted">${{(family.edition_classes || ["custom"]).join(", ")}} | ${{family.edition_scope || "n/a"}} | ${{family.load_mode}}</div>
            <div>${{issueSummaryLabel(family)}}</div>
            <div class="muted">${{family.object_class_count}} objects, ${{family.interaction_class_count}} interactions, ${{family.datatype_count}} datatypes</div>
          </div>
          <div class="family-card-foot">
            ${{family.validation_verdict ? statusPill(family.validation_verdict.replaceAll(" ", "-")) : ""}}
          </div>
        `;
        card.onclick = () => {{
          selectedCatalogName = catalogName;
          selectedNodeName = null;
          selectedSearchName = null;
          refreshSelectionViews();
        }};
        host.appendChild(card);
      }}
      if (!host.children.length) {{
        host.innerHTML = emptyState("No catalog items match the current filters.");
      }}
    }}

    function visibleCatalogNames() {{
      return [...document.querySelectorAll("#family-list .family-card strong")]
        .map((node) => node.textContent?.trim())
        .filter(Boolean);
    }}

    function moveCatalogSelection(delta) {{
      const names = visibleCatalogNames();
      if (!names.length) return;
      const currentIndex = Math.max(0, names.indexOf(selectedCatalogName));
      const nextIndex = Math.min(names.length - 1, Math.max(0, currentIndex + delta));
      if (names[nextIndex] === selectedCatalogName) return;
      selectedCatalogName = names[nextIndex];
      selectedNodeName = null;
      selectedSearchName = null;
      refreshSelectionViews();
      document.getElementById("family-list").focus();
    }}

    function syncDiffSelectionToCatalog() {{
      const left = document.getElementById("left-family");
      const right = document.getElementById("right-family");
      if (!left || !right) return;
      const names = [
        ...snapshot.families.map((family) => family.scenario_family),
        ...customLoadSets().map((loadSet) => loadSet.name),
      ];
      if (!names.length) return;
      if (selectedCatalogName && names.includes(selectedCatalogName)) {{
        left.value = selectedCatalogName;
      }}
      const fallback = names.find((name) => name !== left.value) || left.value;
      if (!names.includes(right.value) || right.value === left.value) {{
        right.value = fallback;
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
      const validationCommands = family.validation_command ? [{{ label: "validation command", command: family.validation_command }}] : [];
      host.innerHTML = `
        <div class="surface-kicker">Overview</div>
        <div class="summary-title">
          <strong>${{title}}</strong>
          ${{statusPill(catalogStatus(family))}}
          ${{family.validation_verdict ? statusPill(family.validation_verdict.replaceAll(" ", "-")) : ""}}
        </div>
        ${{
          renderActionBar([
            {{ label: "Open Validation Report", kind: "primary", href: family.validation_html_path, disabled: !family.validation_html_path }},
            {{ label: "Go To Validation", kind: "secondary", workspace: "validation" }},
            {{ label: "Copy Validation Command", kind: "secondary", command: family.validation_command, disabled: !family.validation_command }},
          ])
        }}
        <dl class="kv">
          <dt>Selection</dt><dd>${{title}}</dd>
          <dt>Edition classes</dt><dd>${{(family.edition_classes || ["custom"]).join(", ")}}</dd>
          <dt>Edition scope</dt><dd>${{displayText(family.edition_scope)}}</dd>
          <dt>Baseline kinds</dt><dd>${{(family.baseline_kinds || ["custom"]).join(", ")}}</dd>
          <dt>Load mode</dt><dd>${{family.load_mode}}</dd>
          <dt>Parse status</dt><dd>${{family.parse_status}}${{family.parse_error_kind ? ` (${{family.parse_error_kind}})` : ""}}${{family.parse_error ? `: ${{family.parse_error}}` : ""}}</dd>
          <dt>Next step</dt><dd>${{displayText(family.recommended_next_step)}}</dd>
          <dt>Conflict symbol</dt><dd>${{displayText(family.merge_conflict_symbol)}}</dd>
          <dt>Conflict members</dt><dd>${{displayText(family.merge_conflict_members)}}</dd>
          <dt>Conflict details</dt><dd>${{conflictDetailsBlock(family.merge_conflict_member_details || [])}}</dd>
          <dt>Default load set</dt><dd>${{(family.default_load_set_ids || family.member_ids).join(", ")}}</dd>
          <dt>Module names</dt><dd>${{family.module_names.join(", ")}}</dd>
          <dt>Dimensions</dt><dd>${{displayText(family.dimensions)}}</dd>
        </dl>
        ${{
          renderCommandDrawer("Operator commands", validationCommands, "Validation command unavailable for this selection.")
        }}
        <h3>Validation Files</h3>
        <div class="list">
          ${{
            family.validation_html_path
              ? `<div style="margin-top: 10px;"><a href="${{family.validation_html_path}}" target="_blank" rel="noopener">open validation HTML</a><br>
                 <a href="${{family.validation_md_path}}" target="_blank" rel="noopener">open validation Markdown</a><br>
                 <a href="${{family.validation_json_path}}" target="_blank" rel="noopener">open validation JSON</a></div>`
              : `<div style="margin-top: 10px;">${{emptyState("Validation files are not present in this snapshot.")}}</div>`
          }}
        </div>
        <h3>Source Files</h3>
        <div class="list">${{family.member_paths.map((item) => `<code>${{item}}</code>`).join("")}}</div>
      `;
      wireCopyButtons(host);
      wireActionButtons(host);
      renderTree();
      renderEditFlow();
    }}

    function selectionSearchRows() {{
      return snapshot.search_index.filter((row) => !selectedCatalogName || row.source_name === selectedCatalogName);
    }}

    function currentSearchRows() {{
      const filter = document.getElementById("search-filter").value.trim().toLowerCase();
      const matchesFilter = (row) => {{
        if (!filter) return true;
        return [row.kind, row.name, row.source_name, row.parent_name || "", row.lineage.join(" "), row.edition_classes.join(" "), row.edition_scope]
          .join(" ")
          .toLowerCase()
          .includes(filter);
      }};
      const matchesWorkspaceFocus = (row) => matchesFocus(
        row.kind,
        [row.kind, row.name, row.source_name, row.parent_name || "", row.lineage, row.edition_classes, row.edition_scope, row.load_mode],
        {{ owners: row.baseline_kinds, issue: true, changed: true }},
      );
      const scopedRows = selectionSearchRows().filter((row) => matchesFilter(row) && matchesWorkspaceFocus(row));
      if (scopedRows.length || !filter) return scopedRows.slice(0, 250);
      return snapshot.search_index.filter((row) => matchesFilter(row) && matchesWorkspaceFocus(row)).slice(0, 250);
    }}

    function inferTreeKind(symbol, explicitKind = null) {{
      if (explicitKind === "object" || explicitKind === "interaction") return explicitKind;
      if (!symbol) return null;
      if (symbol.startsWith("HLAinteractionRoot")) return "interaction";
      if (symbol.startsWith("HLAobjectRoot")) return "object";
      const row = currentSearchRows().find((item) => item.name === symbol);
      if (row && (row.kind === "object" || row.kind === "interaction")) return row.kind;
      return null;
    }}

    function jumpToSymbol(symbol, options = {{}}) {{
      if (!symbol) return;
      const explicitKind = options.kind || null;
      const setFilter = options.setFilter !== false;
      if (setFilter) document.getElementById("search-filter").value = symbol;
      selectedSearchName = symbol;
      const kind = inferTreeKind(symbol, explicitKind);
      if (kind) {{
        document.getElementById("tree-kind").value = kind;
        selectedNodeName = symbol;
      }}
      renderWorkspaceMode();
      renderSelectionSummary();
      renderSearch();
      renderTree();
    }}

    function renderSearch() {{
      const tbody = document.getElementById("search-results");
      const rows = currentSearchRows();
      if (!rows.some((row) => row.name === selectedSearchName)) selectedSearchName = rows[0]?.name || null;
      if (!rows.length) {{
        tbody.innerHTML = `<tr><td colspan="3">${{emptyState("No merged names match the current search scope.")}}</td></tr>`;
        return;
      }}
      tbody.innerHTML = rows.map((row) => {{
        const active = row.name === selectedSearchName ? " active" : "";
        return `
          <tr class="search-row${{active}}" data-symbol="${{row.name}}" data-kind="${{row.kind}}">
            <td>${{row.kind}}</td>
            <td><code>${{row.name}}</code><br><span class="muted">${{row.lineage.join(" > ")}}</span></td>
            <td>${{row.source_name}}</td>
          </tr>
        `;
      }}).join("");
      tbody.querySelectorAll(".search-row").forEach((element) => {{
        element.onclick = () => {{
          jumpToSymbol(element.dataset.symbol, {{ kind: element.dataset.kind }});
        }};
      }});
    }}

    function moveSearchSelection(delta) {{
      const rows = currentSearchRows();
      if (!rows.length) return;
      const currentIndex = Math.max(0, rows.findIndex((row) => row.name === selectedSearchName));
      const nextIndex = Math.min(rows.length - 1, Math.max(0, currentIndex + delta));
      const next = rows[nextIndex];
      if (!next) return;
      jumpToSymbol(next.name, {{ kind: next.kind }});
      document.getElementById("search-filter").focus();
    }}

    function formatConflictValue(value) {{
      if (Array.isArray(value)) return value.length ? value.join(", ") : "none";
      if (value && typeof value === "object") return Object.entries(value).map(([key, inner]) => `${{key}}=${{formatConflictValue(inner)}}`).join("; ");
      if (value === null || value === undefined || value === "") return "not available";
      return String(value);
    }}

    function conflictDetailsBlock(details) {{
      if (!details || !details.length) return "<span class='muted'>No member-level detail recorded.</span>";
      return `<div class="cards">${{details.map((detail) => {{
        const tone = detail.baseline_kind === "repo-owned" ? "healthy" : "warning";
        const rows = Object.entries(detail)
          .filter(([key]) => key !== "member")
          .map(([key, value]) => `<div class="muted"><strong>${{key.replaceAll("_", " ")}}:</strong> ${{formatConflictValue(value)}}</div>`)
          .join("");
        return `<div class="card ${{tone}}">
          <div class="card-head">
            <strong>${{detail.member || "member"}}</strong>
            <span class="ownership-note">${{detail.baseline_kind || "ownership unavailable"}}</span>
          </div>
          <div class="card-meta">${{rows}}</div>
        </div>`;
      }}).join("")}}</div>`;
    }}

    function symbolsFromValidationMessages(messages) {{
      if (!messages || !messages.length) return [];
      const candidates = selectionSearchRows()
        .map((row) => row.name)
        .filter((name, index, values) => values.indexOf(name) === index)
        .sort((left, right) => right.length - left.length);
      const found = [];
      for (const symbol of candidates) {{
        if (messages.some((message) => String(message || "").includes(symbol)) && !found.includes(symbol)) {{
          found.push(symbol);
        }}
      }}
      return found.slice(0, 3);
    }}

    function firstValidationSymbol(groups) {{
      for (const group of groups || []) {{
        const symbols = symbolsFromValidationMessages(group.messages || []);
        if (symbols.length) return symbols[0];
      }}
      return null;
    }}

    function renderSymbolActions(symbols) {{
      if (!symbols.length) return "<span class='muted'>no symbol jump</span>";
      return symbols.map((symbol) => `<button class="symbol-link" type="button" data-symbol="${{symbol}}">${{symbol}}</button>`).join("");
    }}

    function wireSymbolJumpButtons(host = document) {{
      host.querySelectorAll(".symbol-link").forEach((element) => {{
        element.onclick = () => {{
          jumpToSymbol(element.dataset.symbol, {{ kind: element.dataset.kind || null }});
        }};
      }});
    }}

    function validationGroupsBlock(groups, owners = []) {{
      if (!groups || !groups.length) return "<span class='muted'>No grouped validation issues are recorded for this selection.</span>";
      const filteredGroups = groups.filter((group) => {{
        const messages = group.messages || [];
        const symbols = symbolsFromValidationMessages(messages);
        return matchesFocus(
          "issue",
          [group.layer, messages, symbols],
          {{ ignoreKind: true, issue: true, changed: true, owners }},
        );
      }});
      if (!filteredGroups.length) return "<span class='muted'>No validation issues match the workspace focus.</span>";
      return `<div class="cards">${{filteredGroups.map((group) => `
        <div class="card ${{group.count ? "warning" : "healthy"}}">
          <div class="card-head">
            <strong>${{group.layer}}</strong>
            <span class="ownership-note">${{group.count}} issue${{group.count === 1 ? "" : "s"}}</span>
          </div>
          <div style="margin: 8px 0;">${{renderSymbolActions(symbolsFromValidationMessages(group.messages || []))}}</div>
          ${{
            (group.messages || []).map((message) => `<div class="muted">${{message}}</div>`).join("")
          }}
        </div>
      `).join("")}}</div>`;
    }}

    function renderConflictWorkspace() {{
      const host = document.getElementById("conflict-panel");
      const family = currentCatalogItem();
      if (!family) {{
        host.textContent = "Select a family or custom load set to inspect conflict state.";
        return;
      }}
      const status = catalogStatus(family);
      const symbol = family.merge_conflict_symbol;
      const canJump = Boolean(symbol);
      const severity = severityClass(status, family.validation_verdict);
      const commandItems = [
        ...(family.validation_command ? [{{ label: "validation command", command: family.validation_command }}] : []),
        ...(family.parse_status !== "browser-pending"
          ? [{{ label: "regenerate diff", command: `./tools/fom-workbench --html --diff ${{family.scenario_family || family.name}}:${{family.scenario_family || family.name}}` }}]
          : []),
      ];
      host.innerHTML = `
        <div class="surface-kicker">Conflict state</div>
        <div class="summary-title">
          <strong>${{family.scenario_family || family.name}}</strong> ${{statusPill(status)}}
        </div>
        <div class="count-grid">
          <div class="count-box ${{severity}}">
            <strong>${{family.merge_conflict_symbol || "No symbol"}}</strong>
            <span class="muted">Conflict symbol</span>
          </div>
          <div class="count-box">
            <strong>${{(family.merge_conflict_members || []).length}}</strong>
            <span class="muted">Members involved</span>
          </div>
          <div class="count-box">
            <strong>${{family.validation_issue_count || 0}}</strong>
            <span class="muted">Validation issues</span>
          </div>
          <div class="count-box">
            <strong>${{ownershipLabel(family)}}</strong>
            <span class="muted">Ownership mix</span>
          </div>
        </div>
        <div class="next-step-box" style="margin-bottom: 12px;">
          <div class="stat-label">Next action</div>
          <div>${{family.recommended_next_step || "n/a"}}</div>
        </div>
        ${{
          renderActionBar([
            {{ label: "Investigate Symbol", kind: "primary", symbol, disabled: !canJump }},
            {{ label: "Prepare Repair", kind: "secondary", workspace: "repair", disabled: !(family.merge_conflict_member_details || []).length }},
            {{ label: "Copy Validation Command", kind: "secondary", command: family.validation_command, disabled: !family.validation_command }},
          ])
        }}
        <p class="muted">Parse status: ${{family.parse_status}}${{family.parse_error_kind ? ` (${{family.parse_error_kind}})` : ""}}</p>
        <p><strong>Validation:</strong> ${{family.validation_verdict || "n/a"}}${{family.validation_issue_count ? ` | issues=${{family.validation_issue_count}}` : ""}}</p>
        <p><strong>Conflict members:</strong> ${{(family.merge_conflict_members || []).join(", ") || "n/a"}}</p>
        <div><strong>Conflict details:</strong>${{conflictDetailsBlock(family.merge_conflict_member_details || [])}}</div>
        ${{
          renderCommandDrawer("Technical commands", commandItems, "No technical commands available for this conflict state.")
        }}
        <div class="builder-grid" style="margin-top: 10px;">
          <button id="conflict-jump-search" type="button" ${{canJump ? "" : "disabled"}}>open in search</button>
          <button id="conflict-copy-symbol" type="button" ${{canJump ? "" : "disabled"}}>pin symbol</button>
        </div>
      `;
      const jumpButton = document.getElementById("conflict-jump-search");
      const focusButton = document.getElementById("conflict-copy-symbol");
      if (jumpButton && canJump) {{
        jumpButton.onclick = () => {{
          jumpToSymbol(symbol, {{ setFilter: true }});
        }};
      }}
      if (focusButton && canJump) {{
        focusButton.onclick = () => {{
          jumpToSymbol(symbol, {{ setFilter: true }});
        }};
      }}
      wireCopyButtons(host);
      wireActionButtons(host);
    }}

    function renderValidationWorkspace() {{
      const host = document.getElementById("validation-panel");
      const family = currentCatalogItem();
      if (!family) {{
        host.textContent = "Select a family or custom load set to inspect validation state.";
        return;
      }}
      const severity = severityClass(catalogStatus(family), family.validation_verdict);
      const firstIssueSymbol = firstValidationSymbol(family.validation_issue_groups || []);
      const commandItems = family.validation_command ? [{{ label: "validation command", command: family.validation_command }}] : [];
      const normalizationRows = family.datatype_normalizations || [];
      host.innerHTML = `
        <div class="surface-kicker">Validation state</div>
        <div class="summary-title">
          <strong>${{family.scenario_family || family.name}}</strong>
          ${{statusPill(catalogStatus(family))}}
          ${{family.validation_verdict ? statusPill(family.validation_verdict.replaceAll(" ", "-")) : ""}}
        </div>
        <div class="count-grid">
          <div class="count-box ${{severity}}">
            <strong>${{family.validation_verdict || "n/a"}}</strong>
            <span class="muted">Verdict</span>
          </div>
          <div class="count-box">
            <strong>${{family.validation_issue_count || 0}}</strong>
            <span class="muted">Issues</span>
          </div>
          <div class="count-box">
            <strong>${{(family.validation_issue_layers || []).length || 0}}</strong>
            <span class="muted">Layers</span>
          </div>
          <div class="count-box">
            <strong>${{ownershipLabel(family)}}</strong>
            <span class="muted">Ownership mix</span>
          </div>
        </div>
        <div class="next-step-box" style="margin-bottom: 12px;">
          <div class="stat-label">Next action</div>
          <div>${{family.validation_issue_count ? "Review the issue groups and jump into the affected symbol." : "Open the validation packet or continue inspection."}}</div>
        </div>
        ${{
          renderActionBar([
            {{ label: "Open Validation Report", kind: "primary", href: family.validation_html_path, disabled: !family.validation_html_path }},
            {{ label: "Investigate First Issue", kind: "secondary", symbol: firstIssueSymbol, disabled: !firstIssueSymbol }},
            {{ label: "Copy Validation Command", kind: "secondary", command: family.validation_command, disabled: !family.validation_command }},
          ])
        }}
        <p><strong>Issue layers:</strong> ${{(family.validation_issue_layers || []).join(", ") || "none"}}</p>
        <div><strong>Datatype normalization:</strong>${{normalizationRows.length
          ? `<div class="list">${{normalizationRows.map((row) => `<div><code>${{row.datatype}}</code> <span class="muted">${{row.category}}</span><br><span class="muted">${{row.source_encoding}} -> ${{row.canonical_encoding}}</span></div>`).join("")}}</div>`
          : `<span class="muted">No source-specific datatype normalization was needed.</span>`}}</div>
        <div><strong>Issue groups:</strong>${{validationGroupsBlock(family.validation_issue_groups || [], family.baseline_kinds || [])}}</div>
        ${{
          renderCommandDrawer("Technical commands", commandItems, "Validation command unavailable for this selection.")
        }}
        <div class="list" style="margin-top: 10px;">
          ${{
            family.validation_html_path
              ? `<a href="${{family.validation_html_path}}" target="_blank" rel="noopener">open validation HTML</a><br>
                 <a href="${{family.validation_md_path}}" target="_blank" rel="noopener">open validation Markdown</a><br>
                 <a href="${{family.validation_json_path}}" target="_blank" rel="noopener">open validation JSON</a>`
              : `<span class="muted">Validation files are not present in this snapshot.</span>`
          }}
        </div>
      `;
      wireSymbolJumpButtons(host);
      wireCopyButtons(host);
      wireActionButtons(host);
    }}

    function currentNodes() {{
      const family = currentCatalogItem();
      if (!family) return [];
      const kind = document.getElementById("tree-kind").value;
      const rows = kind === "interaction" ? family.interaction_nodes : family.object_nodes;
      return rows.filter((row) => matchesFocus(
        kind,
        [row.kind, row.full_name, row.parent_name || "", row.lineage, row.declared_names, row.total_names, row.datatype_hints],
        {{ owners: family.baseline_kinds || [], issue: true, changed: true }},
      ));
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
      if (!rows.length) {{
        panel.innerHTML = emptyState("No hierarchy nodes match the current tree filter.");
        selectedNodeName = null;
        renderNodePanel();
        return;
      }}
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
          selectedSearchName = element.dataset.name;
          renderWorkspaceMode();
          renderSelectionSummary();
          renderTree();
          renderSearch();
          renderNodePanel();
        }};
      }});
      if (!selectedNodeName && rows[0]) {{
        selectedNodeName = rows[0].full_name;
        renderWorkspaceMode();
        renderSelectionSummary();
      }}
      renderNodePanel();
    }}

    function renderNodePanel() {{
      const host = document.getElementById("node-panel");
      const row = currentNodes().find((item) => item.full_name === selectedNodeName);
      if (!row) {{
        host.innerHTML = emptyState("Pin a symbol from search, diff, conflict, or validation to inspect its merged declaration here.");
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

    function selectionLabel(family) {{
      return family.scenario_family || family.name || "selection";
    }}

    function selectionWorkbenchCommand(family) {{
      if (family.name) return `./tools/fom-workbench --html --custom-load-set ${{family.name}}=${{family.member_ids.join(",")}}`;
      return "./tools/fom-workbench --html";
    }}

    function metadataEditCommand(entryId) {{
      const desc = document.getElementById("edit-description").value.trim();
      const keywords = document.getElementById("edit-keywords").value.trim();
      const notes = document.getElementById("edit-notes").value.trim();
      let cmd = `./tools/fom-workbench --edit-entry ${{entryId}}`;
      if (desc) cmd += ` --set-description ${{JSON.stringify(desc)}}`;
      for (const item of keywords.split(",").map((value) => value.trim()).filter(Boolean)) cmd += ` --add-keyword ${{JSON.stringify(item)}}`;
      for (const item of notes.split(",").map((value) => value.trim()).filter(Boolean)) cmd += ` --add-note ${{JSON.stringify(item)}}`;
      return cmd;
    }}

    function repairSuggestions(family) {{
      const suggestions = [];
      const details = family.merge_conflict_member_details || [];
      if (family.parse_error_kind !== "merge" || !details.length) return suggestions;
      if (family.merge_conflict_kind === "simple datatype" && family.merge_conflict_symbol) {{
        for (const detail of details) {{
          if (detail.baseline_kind !== "repo-owned" || !detail.entry_id) {{
            suggestions.push({{
              status: "blocked",
              title: `Blocked member: ${{detail.member || "unknown"}}`,
              summary: `This conflict member is not repo-owned.`,
              targetPath: detail.entry_path || "n/a",
              commands: [],
            }});
            continue;
          }}
          const declaration = detail.declaration || {{}};
          const peer = details.find((item) => item.entry_id !== detail.entry_id && item.declaration && item.declaration.category === "simple");
          if (declaration.category !== "simple" || !peer) {{
            suggestions.push({{
              status: "unsupported",
              title: `Unsupported repair for ${{detail.entry_id}}`,
              summary: `The current repair helper only previews repo-owned simple datatype alignments.`,
              targetPath: detail.entry_path || "n/a",
              commands: [],
            }});
            continue;
          }}
          let editCommand = `./tools/fom-workbench --edit-entry ${{detail.entry_id}}`;
          if (peer.declaration.representation) {{
            editCommand += ` --set-simple-datatype-representation ${{JSON.stringify(`${{family.merge_conflict_symbol}}=${{peer.declaration.representation}}`)}}`;
          }}
          if (peer.declaration.semantics) {{
            editCommand += ` --set-simple-datatype-semantics ${{JSON.stringify(`${{family.merge_conflict_symbol}}=${{peer.declaration.semantics}}`)}}`;
          }}
          suggestions.push({{
            status: "supported",
            title: `Align ${{detail.entry_id}} to ${{peer.entry_id || peer.member || "peer"}}`,
            summary: `Match the repo-owned simple datatype declaration for ${{family.merge_conflict_symbol}} to the peer declaration.`,
            targetPath: detail.entry_path || "n/a",
            commands: [
              editCommand,
              selectionWorkbenchCommand(family),
              family.validation_command || "validation command unavailable",
            ],
          }});
        }}
        return suggestions;
      }}
      suggestions.push({{
        status: "unsupported",
        title: "Unsupported conflict repair",
        summary: `This UI only stages repo-owned simple datatype repair previews right now. Conflict kind: ${{family.merge_conflict_kind || "unknown"}}.`,
        targetPath: "n/a",
        commands: [],
      }});
      return suggestions;
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
        summary.textContent = `This selection has no repo-owned entries. Third-party members remain read-only.`;
      }} else {{
        summary.textContent = `Repo-owned editable entries: ${{editable.map((entry) => entry.id).join(", ")}}. Third-party members remain read-only.`;
      }}
      if (blocked.length) {{
        summary.textContent += ` Blocked: ${{blocked.map((entry) => entry.id).join(", ")}}`;
      }}
      const firstEditable = editable[0];
      const repairCards = repairSuggestions(family);
      const repairHtml = repairCards.length
        ? `<div class="cards">${{repairCards.map((card) => `
            <div class="card ${{severityClass(card.status)}}">
              <div class="card-head">
                <strong>${{card.title}}</strong>
                ${{statusPill(card.status)}}
              </div>
              <span class="muted">${{card.summary}}</span><br>
              <span class="muted">Target file: <code>${{card.targetPath}}</code></span>
              ${{
                renderActionBar([
                  {{ label: "Copy Repair Command", kind: "primary", command: card.commands[0], disabled: !card.commands[0] }},
                  {{ label: "Copy Regenerate Command", kind: "secondary", command: card.commands[1], disabled: !card.commands[1] }},
                  {{ label: "Copy Validation Command", kind: "secondary", command: card.commands[2], disabled: !card.commands[2] }},
                ])
              }}
              ${{
                renderCommandDrawer(
                  "Technical commands",
                  card.commands.map((item, index) => ({{
                    label: index === 0 ? "repair command" : index === 1 ? "regenerate workbench" : "rerun validation",
                    command: item,
                  }})),
                  "No executable repair preview for this card.",
                )
              }}
            </div>
          `).join("")}}</div>`
        : emptyState("No repair preview is available for this selection yet.");
      if (!firstEditable) {{
        command.innerHTML = `${{repairHtml}}<div class="list" style="margin-top: 10px;">${{emptyState("No metadata edit preview is available for this selection.")}}</div>`;
        wireCopyButtons(command);
        wireActionButtons(command);
        return;
      }}
      const metadataCommand = metadataEditCommand(firstEditable.id);
      command.innerHTML = `
        ${{repairHtml}}
        <div class="card" style="margin-top: 10px;">
          <div class="card-head">
            <strong>Metadata edit preview for ${{firstEditable.id}}</strong>
            <span class="ownership-note">repo-owned</span>
          </div>
          ${{
            renderActionBar([
              {{ label: "Copy Metadata Edit Command", kind: "primary", command: metadataCommand }},
            ])
          }}
          ${{
            renderCommandDrawer(
              "Technical commands",
              [{{ label: "metadata edit command", command: metadataCommand }}],
            )
          }}
        </div>
      `;
      wireCopyButtons(command);
      wireActionButtons(command);
    }}

    function renderBuilder() {{
      const nameBox = document.getElementById("builder-name");
      const filter = document.getElementById("builder-filter").value.trim().toLowerCase();
      const listHost = document.getElementById("builder-entry-list");
      const savedHost = document.getElementById("builder-saved");
      const commandHost = document.getElementById("builder-command");
      const selectedHost = document.getElementById("builder-selected");
      const healthHost = document.getElementById("builder-health");
      const rows = snapshot.entries.filter((entry) => {{
        if (!filter) return true;
        return [entry.id, entry.scenario_family, entry.edition_class, entry.edition_scope, entry.path, entry.load_mode, entry.baseline_kind]
          .join(" ")
          .toLowerCase()
          .includes(filter);
      }});
      listHost.innerHTML = rows.map((entry) => {{
        const checked = builderHas(entry.id) ? "checked" : "";
        return `<label><input type="checkbox" data-entry-id="${{entry.id}}" ${{checked}}> <code>${{entry.id}}</code> <span class="muted">${{entry.scenario_family}} | ${{entry.edition_class}} | ${{entry.edition_scope}} | ${{entry.load_mode}}</span></label>`;
      }}).join("");
      listHost.querySelectorAll("input[type=checkbox]").forEach((node) => {{
        node.addEventListener("change", () => {{
          if (node.checked) builderAdd(node.dataset.entryId);
          else builderRemove(node.dataset.entryId);
          renderBuilder();
        }});
      }});
      const selectedIds = [...builderSelectedMemberIds];
      const selectedMembers = selectedIds.map((id) => entryMap.get(id)).filter(Boolean);
      const health = evaluateBuilderSelection(selectedIds);
      healthHost.innerHTML = `
        ${{statusPill(health.label.replaceAll(" ", "-"))}}
        <div class="muted">edition scope: ${{health.editionScope}} | baselines: ${{health.baselineKinds.join(", ") || "n/a"}} | load modes: ${{health.loadModes.join(", ") || "n/a"}}</div>
        ${{health.warnings.map((item) => `<div class="muted">${{item}}</div>`).join("")}}
      `;
      selectedHost.innerHTML = selectedMembers.length
        ? selectedMembers.map((entry, index) => `
            <div style="margin-bottom: 8px;">
              <strong>${{index + 1}}. <code>${{entry.id}}</code></strong>
              <span class="muted">${{entry.scenario_family}} | ${{entry.load_mode}}</span><br>
              <button type="button" data-move="up" data-entry-id="${{entry.id}}" ${{index === 0 ? "disabled" : ""}}>move up</button>
              <button type="button" data-move="down" data-entry-id="${{entry.id}}" ${{index === selectedMembers.length - 1 ? "disabled" : ""}}>move down</button>
            </div>
          `).join("")
        : "<span class='muted'>Select baseline entries to build an ordered load set.</span>";
      selectedHost.querySelectorAll("button[data-move]").forEach((node) => {{
        node.addEventListener("click", () => {{
          builderMove(node.dataset.entryId, node.dataset.move === "up" ? -1 : 1);
          renderBuilder();
        }});
      }});
      const candidateName = nameBox.value.trim();
      if (!selectedIds.length) {{
        commandHost.innerHTML = emptyState("Select one or more baseline entries to build a named custom load set.");
      }} else if (!candidateName) {{
        commandHost.innerHTML = renderCommandList([{{ label: "preview custom load-set command", command: customLoadSetCommand("custom-name", selectedIds) }}]);
      }} else {{
        commandHost.innerHTML = renderCommandList([{{ label: "custom load-set command", command: customLoadSetCommand(candidateName, selectedIds) }}]);
      }}
      wireCopyButtons(commandHost);
      if (!browserCustomLoadSets.length) {{
        savedHost.innerHTML = emptyState("Saved browser load sets appear here.");
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
            builderSelectedMemberIds = [...row.member_ids];
            renderBuilder();
            return;
          }}
          if (button.dataset.action === "inspect") {{
            document.getElementById("catalog-mode").value = "custom-load-set";
            selectedCatalogKind = "custom-load-set";
            selectedCatalogName = row.name;
            selectedNodeName = null;
            selectedSearchName = null;
            setDiffSelectors();
            refreshSelectionViews();
            return;
          }}
          browserCustomLoadSets = browserCustomLoadSets.filter((item) => item.name !== row.name);
          saveBrowserCustomLoadSets();
          if (selectedCatalogKind === "custom-load-set" && selectedCatalogName === row.name) {{
            selectedCatalogName = customLoadSets()[0]?.name || null;
          }}
          renderBuilder();
          setDiffSelectors();
          refreshSelectionViews();
        }});
      }});
    }}

    function saveBuilderSelection() {{
      const name = document.getElementById("builder-name").value.trim();
      const memberIds = [...builderSelectedMemberIds];
      const commandHost = document.getElementById("builder-command");
      if (!name) {{
        commandHost.innerHTML = emptyState("Name the custom load set before saving it in the browser.");
        return;
      }}
      if (!memberIds.length) {{
        commandHost.innerHTML = emptyState("Select at least one baseline entry before saving a custom load set.");
        return;
      }}
      if (fixedFamilyNames.has(name) || fixedCustomLoadSetNames.has(name)) {{
        commandHost.innerHTML = emptyState(`${{name}} is already used by a family or generated custom load set. Pick another name.`);
        return;
      }}
      browserCustomLoadSets = browserCustomLoadSets.filter((row) => row.name !== name);
      browserCustomLoadSets.push({{ name, member_ids: memberIds }});
      browserCustomLoadSets.sort((left, right) => left.name.localeCompare(right.name));
      saveBrowserCustomLoadSets();
      selectedCatalogKind = "custom-load-set";
      selectedCatalogName = name;
      selectedNodeName = null;
      selectedSearchName = null;
      renderBuilder();
      setDiffSelectors();
      refreshSelectionViews();
    }}

    function exportBuilderSets() {{
      const transfer = document.getElementById("builder-transfer");
      const commandHost = document.getElementById("builder-command");
      if (!browserCustomLoadSets.length) {{
        commandHost.innerHTML = emptyState("There are no browser-saved load sets to export.");
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
      commandHost.innerHTML = emptyState("Exported browser-saved custom load sets to the transfer box and download prompt.");
    }}

    function importBuilderSets() {{
      const transfer = document.getElementById("builder-transfer");
      const commandHost = document.getElementById("builder-command");
      const raw = transfer.value.trim();
      if (!raw) {{
        commandHost.innerHTML = emptyState("Paste exported custom load set JSON into the transfer box before importing.");
        return;
      }}
      let parsed;
      try {{
        parsed = JSON.parse(raw);
      }} catch (_error) {{
        commandHost.innerHTML = emptyState("Import JSON is malformed.");
        return;
      }}
      const imported = normalizeBrowserCustomLoadSets(parsed);
      if (!imported.length) {{
        commandHost.innerHTML = emptyState("Import JSON did not contain any valid browser custom load sets.");
        return;
      }}
      const merged = new Map(browserCustomLoadSets.map((row) => [row.name, row]));
      for (const row of imported) merged.set(row.name, row);
      browserCustomLoadSets = [...merged.values()].sort((left, right) => left.name.localeCompare(right.name));
      saveBrowserCustomLoadSets();
      renderBuilder();
      setDiffSelectors();
      refreshSelectionViews();
      commandHost.innerHTML = emptyState(`Imported ${{imported.length}} browser custom load set(s).`);
    }}

    function diffKey(left, right) {{
      return `${{left}}::${{right}}`;
    }}

    function setDiffSelectors() {{
      const left = document.getElementById("left-family");
      const right = document.getElementById("right-family");
      const names = [
        ...snapshot.families.map((family) => family.scenario_family),
        ...customLoadSets().map((loadSet) => loadSet.name),
      ];
      const options = names.map((name) => `<option value="${{name}}">${{name}}</option>`).join("");
      left.innerHTML = options;
      right.innerHTML = options;
      left.value = selectedCatalogName && names.includes(selectedCatalogName) ? selectedCatalogName : (snapshot.families[0]?.scenario_family || "");
      right.value = customLoadSets()[0]?.name || snapshot.families[1]?.scenario_family || snapshot.families[0]?.scenario_family || "";
      syncDiffSelectionToCatalog();
      left.onchange = () => {{
        renderDiff();
      }};
      right.onchange = () => {{
        renderDiff();
      }};
    }}

    function loadSetByName(name) {{
      return customLoadSets().find((row) => row.name === name) || null;
    }}

    function renderDiff() {{
      const left = document.getElementById("left-family").value;
      const right = document.getElementById("right-family").value;
      const host = document.getElementById("diff-panel");
      rememberComparison(left, right);
      renderRecentComparisons();
      const customLeft = document.getElementById("custom-left").value.trim();
      const customRight = document.getElementById("custom-right").value.trim();
      if (customLeft || customRight) {{
        const diffCommand = `./tools/fom-workbench --html --custom-load-set custom-left=${{customLeft}} --custom-load-set custom-right=${{customRight}} --diff custom-left:custom-right`;
        host.innerHTML = `<p class="muted">Custom load-set diffing is generated by rerunning the tool with named sets.</p>
          ${{renderActionBar([{{ label: "Copy Regenerate Diff Command", kind: "primary", command: diffCommand }}])}}
          ${{renderCommandDrawer("Operator commands", [{{ label: "regenerate custom diff", command: diffCommand }}])}}`;
        wireCopyButtons(host);
        wireActionButtons(host);
        return;
      }}
      if (!left || !right || left === right) {{
        host.innerHTML = emptyState("Select two distinct families or named load sets to compare.");
        return;
      }}
      const diff = diffMap.get(diffKey(left, right)) || diffMap.get(diffKey(right, left));
      if (!diff) {{
        const leftLoadSet = loadSetByName(left);
        const rightLoadSet = loadSetByName(right);
        if (leftLoadSet || rightLoadSet) {{
          const leftCommand = leftLoadSet ? customLoadSetCommand(leftLoadSet.name, leftLoadSet.member_ids) : null;
          const rightCommand = rightLoadSet ? customLoadSetCommand(rightLoadSet.name, rightLoadSet.member_ids) : null;
          const regenCommand = `./tools/fom-workbench --html${{leftLoadSet ? ` --custom-load-set ${{leftLoadSet.name}}=${{leftLoadSet.member_ids.join(",")}}` : ""}}${{rightLoadSet ? ` --custom-load-set ${{rightLoadSet.name}}=${{rightLoadSet.member_ids.join(",")}}` : ""}} --diff ${{left}}:${{right}}`;
          host.innerHTML = `
            <p class="muted">This snapshot does not contain a precomputed diff for the selected pair.</p>
            ${{
              renderActionBar([
                {{ label: "Copy Regenerate Diff Command", kind: "primary", command: regenCommand }},
                {{ label: `Copy ${{left}} Load Set`, kind: "secondary", command: leftCommand, disabled: !leftCommand }},
                {{ label: `Copy ${{right}} Load Set`, kind: "secondary", command: rightCommand, disabled: !rightCommand }},
              ])
            }}
            ${{
              renderCommandDrawer("Operator commands", [
                ...(leftCommand ? [{{ label: `recreate ${{leftLoadSet.name}}`, command: leftCommand }}] : []),
                ...(rightCommand ? [{{ label: `recreate ${{rightLoadSet.name}}`, command: rightCommand }}] : []),
                {{ label: "regenerate diff", command: regenCommand }},
              ])
            }}
          `;
          wireCopyButtons(host);
          wireActionButtons(host);
          return;
        }}
        host.innerHTML = emptyState("This snapshot does not contain a diff for the selected pair.");
        return;
      }}
      const leftLoadSet = loadSetByName(left);
      const rightLoadSet = loadSetByName(right);
      if (!diff.comparable) {{
        host.innerHTML = `
          <p><strong>${{diff.left_family}}</strong> vs <strong>${{diff.right_family}}</strong></p>
          <p class="muted">This comparison cannot be materialized from the current snapshot: ${{displayText(diff.reason)}}</p>
          ${{
            renderActionBar([
              {{ label: "Go To Conflict", kind: "primary", workspace: "conflict" }},
              {{ label: "Investigate Left Conflict", kind: "secondary", symbol: diff.left_merge_conflict_symbol, disabled: !diff.left_merge_conflict_symbol }},
              {{ label: "Investigate Right Conflict", kind: "secondary", symbol: diff.right_merge_conflict_symbol, disabled: !diff.right_merge_conflict_symbol }},
            ])
          }}
          <div class="split">
            <div>
              <h3>Left Side</h3>
              <p><strong>Status:</strong> ${{diff.left_parse_status}}${{diff.left_parse_error_kind ? ` (${{diff.left_parse_error_kind}})` : ""}}</p>
              <p><strong>Next step:</strong> ${{diff.left_recommended_next_step || "n/a"}}</p>
              <p><strong>Conflict symbol:</strong> ${{diff.left_merge_conflict_symbol || "n/a"}}</p>
              <div>${{renderSymbolActions(diff.left_merge_conflict_symbol ? [diff.left_merge_conflict_symbol] : [])}}</div>
              <p><strong>Conflict members:</strong> ${{(diff.left_merge_conflict_members || []).join(", ") || "n/a"}}</p>
              <div><strong>Conflict details:</strong>${{conflictDetailsBlock(diff.left_merge_conflict_member_details || [])}}</div>
              <p class="muted">${{diff.left_parse_error || "No additional error detail."}}</p>
            </div>
            <div>
              <h3>Right Side</h3>
              <p><strong>Status:</strong> ${{diff.right_parse_status}}${{diff.right_parse_error_kind ? ` (${{diff.right_parse_error_kind}})` : ""}}</p>
              <p><strong>Next step:</strong> ${{diff.right_recommended_next_step || "n/a"}}</p>
              <p><strong>Conflict symbol:</strong> ${{diff.right_merge_conflict_symbol || "n/a"}}</p>
              <div>${{renderSymbolActions(diff.right_merge_conflict_symbol ? [diff.right_merge_conflict_symbol] : [])}}</div>
              <p><strong>Conflict members:</strong> ${{(diff.right_merge_conflict_members || []).join(", ") || "n/a"}}</p>
              <div><strong>Conflict details:</strong>${{conflictDetailsBlock(diff.right_merge_conflict_member_details || [])}}</div>
              <p class="muted">${{diff.right_parse_error || "No additional error detail."}}</p>
            </div>
          </div>
        `;
        wireSymbolJumpButtons(host);
        wireCopyButtons(host);
        wireActionButtons(host);
        return;
      }}
      const counts = {{
        objects: (diff.only_left_object_classes || []).length + (diff.only_right_object_classes || []).length,
        interactions: (diff.only_left_interaction_classes || []).length + (diff.only_right_interaction_classes || []).length,
        datatypes: (diff.only_left_datatype_names || []).length + (diff.only_right_datatype_names || []).length,
        dimensions: (diff.only_left_dimensions || []).length + (diff.only_right_dimensions || []).length,
      }};
      const focusedLeftObjects = (diff.only_left_object_classes || []).filter((item) => matchesFocus("object", [item], {{ changed: true, issue: true }}));
      const focusedRightObjects = (diff.only_right_object_classes || []).filter((item) => matchesFocus("object", [item], {{ changed: true, issue: true }}));
      const focusedLeftInteractions = (diff.only_left_interaction_classes || []).filter((item) => matchesFocus("interaction", [item], {{ changed: true, issue: true }}));
      const focusedRightInteractions = (diff.only_right_interaction_classes || []).filter((item) => matchesFocus("interaction", [item], {{ changed: true, issue: true }}));
      const focusedLeftDatatypes = (diff.only_left_datatype_names || []).filter((item) => matchesFocus("datatype", [item], {{ changed: true, issue: true }}));
      const focusedRightDatatypes = (diff.only_right_datatype_names || []).filter((item) => matchesFocus("datatype", [item], {{ changed: true, issue: true }}));
      const focusedLeftDimensions = (diff.only_left_dimensions || []).filter((item) => matchesFocus("dimension", [item], {{ changed: true, issue: true }}));
      const focusedRightDimensions = (diff.only_right_dimensions || []).filter((item) => matchesFocus("dimension", [item], {{ changed: true, issue: true }}));
      const showObjects = focusedLeftObjects.length || focusedRightObjects.length || !focusIsActive() || focusKind === "object";
      const showInteractions = focusedLeftInteractions.length || focusedRightInteractions.length || !focusIsActive() || focusKind === "interaction";
      const showDatatypes = focusedLeftDatatypes.length || focusedRightDatatypes.length || focusKind === "datatype";
      const showDimensions = focusedLeftDimensions.length || focusedRightDimensions.length || focusKind === "dimension";
      host.innerHTML = `
        <p><strong>${{diff.left_family}}</strong> vs <strong>${{diff.right_family}}</strong></p>
        <p class="muted">${{diff.left_kind}} vs ${{diff.right_kind}} | left members: ${{diff.left_member_ids.join(", ")}} | right members: ${{diff.right_member_ids.join(", ")}}</p>
        ${{
          renderActionBar([
            {{ label: "Go To Validation", kind: "primary", workspace: "validation" }},
            {{ label: "Investigate First Left Object", kind: "secondary", symbol: diff.only_left_object_classes[0], symbolKind: "object", disabled: !(diff.only_left_object_classes || []).length }},
            {{ label: "Investigate First Right Object", kind: "secondary", symbol: diff.only_right_object_classes[0], symbolKind: "object", disabled: !(diff.only_right_object_classes || []).length }},
          ])
        }}
        <div class="count-grid">
          <div class="count-box">
            <strong>${{counts.objects}}</strong>
            <span class="muted">Object deltas</span>
          </div>
          <div class="count-box">
            <strong>${{counts.interactions}}</strong>
            <span class="muted">Interaction deltas</span>
          </div>
          <div class="count-box">
            <strong>${{counts.datatypes}}</strong>
            <span class="muted">Datatype deltas</span>
          </div>
          <div class="count-box">
            <strong>${{counts.dimensions}}</strong>
            <span class="muted">Dimension deltas</span>
          </div>
        </div>
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
        ${{
          showObjects
            ? `<div class="split">
                <div>
                  <h3>Only Left Objects</h3>
                  <div class="list">${{focusedLeftObjects.slice(0, 120).map((item) => `<button class="symbol-link" type="button" data-symbol="${{item}}" data-kind="object">${{item}}</button>`).join("") || "<span class='muted'>none</span>"}}</div>
                </div>
                <div>
                  <h3>Only Right Objects</h3>
                  <div class="list">${{focusedRightObjects.slice(0, 120).map((item) => `<button class="symbol-link" type="button" data-symbol="${{item}}" data-kind="object">${{item}}</button>`).join("") || "<span class='muted'>none</span>"}}</div>
                </div>
              </div>`
            : ""
        }}
        ${{
          showInteractions
            ? `<div class="split" style="margin-top: 14px;">
                <div>
                  <h3>Only Left Interactions</h3>
                  <div class="list">${{focusedLeftInteractions.slice(0, 120).map((item) => `<button class="symbol-link" type="button" data-symbol="${{item}}" data-kind="interaction">${{item}}</button>`).join("") || "<span class='muted'>none</span>"}}</div>
                </div>
                <div>
                  <h3>Only Right Interactions</h3>
                  <div class="list">${{focusedRightInteractions.slice(0, 120).map((item) => `<button class="symbol-link" type="button" data-symbol="${{item}}" data-kind="interaction">${{item}}</button>`).join("") || "<span class='muted'>none</span>"}}</div>
                </div>
              </div>`
            : ""
        }}
        ${{
          showDatatypes
            ? `<div class="split" style="margin-top: 14px;">
                <div>
                  <h3>Only Left Datatypes</h3>
                  <div class="list">${{focusedLeftDatatypes.slice(0, 120).map((item) => `<code>${{item}}</code>`).join("") || "<span class='muted'>none</span>"}}</div>
                </div>
                <div>
                  <h3>Only Right Datatypes</h3>
                  <div class="list">${{focusedRightDatatypes.slice(0, 120).map((item) => `<code>${{item}}</code>`).join("") || "<span class='muted'>none</span>"}}</div>
                </div>
              </div>`
            : ""
        }}
        ${{
          showDimensions
            ? `<div class="split" style="margin-top: 14px;">
                <div>
                  <h3>Only Left Dimensions</h3>
                  <div class="list">${{focusedLeftDimensions.slice(0, 120).map((item) => `<code>${{item}}</code>`).join("") || "<span class='muted'>none</span>"}}</div>
                </div>
                <div>
                  <h3>Only Right Dimensions</h3>
                  <div class="list">${{focusedRightDimensions.slice(0, 120).map((item) => `<code>${{item}}</code>`).join("") || "<span class='muted'>none</span>"}}</div>
                </div>
              </div>`
            : ""
        }}
        ${{focusIsActive() && !showObjects && !showInteractions && !showDatatypes && !showDimensions ? emptyState("No diff deltas match the workspace focus.") : ""}}
        `;
      wireSymbolJumpButtons(host);
      wireCopyButtons(host);
      wireActionButtons(host);
    }}

    document.getElementById("family-filter").addEventListener("input", renderFamilyList);
    document.getElementById("family-filter").addEventListener("keydown", (event) => {{
      if (event.key === "ArrowDown") {{
        event.preventDefault();
        moveCatalogSelection(1);
      }}
    }});
    document.getElementById("status-filter").addEventListener("change", renderFamilyList);
    document.getElementById("edition-filter").addEventListener("change", renderFamilyList);
    document.getElementById("baseline-filter").addEventListener("change", renderFamilyList);
    document.getElementById("load-mode-filter").addEventListener("change", renderFamilyList);
    document.getElementById("catalog-mode").addEventListener("change", (event) => {{
      selectedCatalogKind = event.target.value;
      selectedCatalogName = selectedCatalogKind === "custom-load-set"
        ? (customLoadSets()[0]?.name || null)
        : (snapshot.families[0]?.scenario_family || null);
      selectedNodeName = null;
      selectedSearchName = null;
      refreshSelectionViews();
    }});
    document.getElementById("family-list").addEventListener("keydown", (event) => {{
      if (event.key === "ArrowDown") {{
        event.preventDefault();
        moveCatalogSelection(1);
      }} else if (event.key === "ArrowUp") {{
        event.preventDefault();
        moveCatalogSelection(-1);
      }}
    }});
    document.getElementById("search-filter").addEventListener("input", renderSearch);
    document.getElementById("search-filter").addEventListener("keydown", (event) => {{
      if (event.key === "ArrowDown") {{
        event.preventDefault();
        moveSearchSelection(1);
      }} else if (event.key === "ArrowUp") {{
        event.preventDefault();
        moveSearchSelection(-1);
      }}
    }});
    document.getElementById("tree-filter").addEventListener("input", renderTree);
    document.getElementById("tree-kind").addEventListener("change", () => {{
      selectedNodeName = null;
      renderWorkspaceMode();
      renderSelectionSummary();
      renderTree();
    }});
    document.getElementById("edit-description").addEventListener("input", renderEditFlow);
    document.getElementById("edit-keywords").addEventListener("input", renderEditFlow);
    document.getElementById("edit-notes").addEventListener("input", renderEditFlow);
    document.getElementById("builder-filter").addEventListener("input", renderBuilder);
    document.getElementById("builder-name").addEventListener("input", renderBuilder);
    document.getElementById("builder-save").addEventListener("click", saveBuilderSelection);
    document.getElementById("builder-clear").addEventListener("click", () => {{
      builderSelectedMemberIds = [];
      document.getElementById("builder-name").value = "";
      renderBuilder();
    }});
    document.getElementById("builder-export").addEventListener("click", exportBuilderSets);
    document.getElementById("builder-import").addEventListener("click", importBuilderSets);
    document.getElementById("custom-left").addEventListener("input", renderDiff);
    document.getElementById("custom-right").addEventListener("input", renderDiff);
    document.querySelectorAll(".workspace-tab").forEach((button) => {{
      button.addEventListener("click", () => {{
        currentWorkspaceMode = button.dataset.workspace;
        renderWorkspaceMode();
        renderSelectionSummary();
        updateDeepLinkHash();
      }});
    }});
    document.querySelectorAll(".focus-chip").forEach((button) => {{
      button.addEventListener("click", () => {{
        focusKind = button.dataset.focusKind || "all";
        rerenderFocusedViews();
      }});
    }});
    document.getElementById("workspace-focus-filter").addEventListener("input", (event) => {{
      focusSelector = event.target.value;
      rerenderFocusedViews();
    }});
    document.getElementById("focus-apply").addEventListener("click", applyAdvancedFocusForm);
    document.getElementById("focus-clear").addEventListener("click", clearFocus);
    document.getElementById("focus-save-preset").addEventListener("click", saveCurrentFocusPreset);
    setCapabilities();
    renderBuilder();
    setDiffSelectors();
    renderFocusControls();
    applyInitialDeepLink();
    refreshSelectionViews();
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
